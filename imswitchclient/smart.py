"""Building blocks for closed-loop ("smart") microscopy from a notebook.

Everything here works on plain numpy images and on two callables - one that
returns an image, one that moves the stage - so it is independent of the
transport and testable without a microscope:

- `phase_correlate`         image shift between two frames, sub-pixel
- `StageCameraCalibration`  pixel offsets <-> stage moves, measured on the live
                            images (sign, rotation and flip included)
- `SafetyBox`               keeps closed-loop moves inside a square around the start
- `find_objects`            blob detection on a background-flattened frame
- `EmptyFieldReference`     "how much of this field of view is sample?",
                            measured against a frame of empty glass
- `Mosaic`                  frames placed by stage position, for overviews

`make_snap` / `make_relative_mover` build the two callables from an
`ImSwitchClient`.

Units: images are indexed (row, col) = (y, x) in pixels, stage moves are µm in
ImSwitch's user frame.
"""
import json
import time

import cv2
import numpy as np


# --------------------------------------------------------------------------- #
# images                                                                       #
# --------------------------------------------------------------------------- #
def to_gray(image):
    """float32 single-channel copy of a 2D or RGB(A) frame"""
    image = np.asarray(image)
    if image.ndim == 3:
        image = image[..., :3].mean(axis=2)
    return image.astype(np.float32)


def phase_correlate(reference, moved, highpass_sigma=1.0):
    """Shift of the content of `moved` relative to `reference`, in pixels.

    Returns `(dy, dx, confidence)`: `moved` ~ `reference` translated by
    (+dy, +dx). `confidence` is the height of the normalised correlation peak:
    typically 0.1-0.5 for a clean shift (it drops as the overlap shrinks),
    below ~0.05 when the frames do not overlap or are featureless. Shifts are
    found up to half the frame size.
    """
    a, b = to_gray(reference), to_gray(moved)
    if a.shape != b.shape:
        raise ValueError(f"frame shapes differ: {a.shape} vs {b.shape}")
    if highpass_sigma:
        # suppress uneven illumination, which otherwise dominates the peak
        a = a - cv2.GaussianBlur(a, (0, 0), 20 * highpass_sigma)
        b = b - cv2.GaussianBlur(b, (0, 0), 20 * highpass_sigma)
    window = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1])).astype(np.float32)
    fa = np.fft.fft2((a - a.mean()) * window)
    fb = np.fft.fft2((b - b.mean()) * window)
    cross = np.conj(fa) * fb
    cross /= np.abs(cross) + 1e-12
    corr = np.real(np.fft.ifft2(cross))
    py, px = np.unravel_index(np.argmax(corr), corr.shape)
    peak = float(corr[py, px])

    def subpixel(c_minus, c0, c_plus):
        denom = c_minus - 2 * c0 + c_plus
        return 0.0 if abs(denom) < 1e-12 else 0.5 * (c_minus - c_plus) / denom

    h, w = corr.shape
    dy = py + subpixel(corr[(py - 1) % h, px], peak, corr[(py + 1) % h, px])
    dx = px + subpixel(corr[py, (px - 1) % w], peak, corr[py, (px + 1) % w])
    if dy > h / 2:
        dy -= h
    if dx > w / 2:
        dx -= w
    return float(dy), float(dx), peak


class EmptyFieldReference:
    """What an empty field of view looks like, to tell sample from background.

    Built from one or more frames of empty glass taken with the exposure and
    illumination you will scan with. `coverage(frame)` is the fraction of a
    frame (0..1) that differs from it by more than `k` times the noise,
    after smoothing over `sigma` px. Because the comparison is per pixel,
    vignetting and fixed background patterns cancel, and both brighter
    (fluorescence, darkfield) and darker (absorbing, brightfield) sample
    counts. A few specks of dust cover little area and score low.
    """

    def __init__(self, empty_frames, sigma=2.0, k=4.0):
        frames = [to_gray(f) for f in (empty_frames if isinstance(empty_frames, (list, tuple))
                                       else [empty_frames])]
        self.sigma, self.k = sigma, k
        smoothed = [cv2.GaussianBlur(f, (0, 0), sigma) for f in frames]
        self.level = np.mean(smoothed, axis=0)
        # How much an empty field varies at scales below ~12 sigma: camera
        # noise plus any faint texture of the glass or medium. That texture
        # moves with the stage, so it does not cancel against the reference
        # and has to be tolerated; slow vignetting is above this scale and
        # does cancel.
        residual = smoothed[0] - cv2.GaussianBlur(smoothed[0], (0, 0), 12 * sigma)
        # away from the edges, where the wide blur misreads a vignetting slope
        h, w = residual.shape
        m = min(int(24 * sigma), h // 4, w // 4)
        variation = float(np.std(residual[m:h - m, m:w - m]))
        span = np.percentile(self.level, 99.5) - np.percentile(self.level, 0.5)
        variation = max(variation, 1e-3 * span, 1e-6)
        # a new frame and the averaged reference both carry it
        self.spread = float(variation * np.sqrt(1 + 1 / len(frames)))

    def difference_mask(self, frame):
        g = cv2.GaussianBlur(to_gray(frame), (0, 0), self.sigma)
        if g.shape != self.level.shape:
            raise ValueError(f"frame {g.shape} does not match the reference {self.level.shape}")
        return np.abs(g - self.level) > self.k * self.spread

    def coverage(self, frame):
        return float(self.difference_mask(frame).mean())


def foreground_mask(image, k=3.0, background_sigma=25.0, dark_objects=False, open_px=2):
    """Boolean mask of pixels that stand out from a smooth background.

    Threshold = median + k * robust std (MAD) of the background-flattened
    frame. `dark_objects=True` for absorbing objects on a bright field.
    """
    g = to_gray(image)
    flat = g - cv2.GaussianBlur(g, (0, 0), background_sigma)
    if dark_objects:
        flat = -flat
    med = np.median(flat)
    mad = np.median(np.abs(flat - med)) * 1.4826 + 1e-6
    mask = (flat > med + k * mad).astype(np.uint8)
    if open_px:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * open_px + 1, 2 * open_px + 1))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    return mask.astype(bool)


def find_objects(image, min_area=20, max_area=None, **mask_kwargs):
    """Connected bright (or dark) blobs, largest first.

    Returns dicts with `y`, `x` (centroid, px), `area` (px), `bbox`
    (x, y, w, h) and `offset` = (dy, dx) of the centroid from the frame centre.
    `mask_kwargs` go to `foreground_mask`.
    """
    mask = foreground_mask(image, **mask_kwargs)
    n, _labels, stats, centroids = cv2.connectedComponentsWithStats(mask.astype(np.uint8), 8)
    cy, cx = (mask.shape[0] - 1) / 2, (mask.shape[1] - 1) / 2
    objects = []
    for i in range(1, n):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area < min_area or (max_area is not None and area > max_area):
            continue
        x, y = centroids[i]
        objects.append({"y": float(y), "x": float(x), "area": area,
                        "bbox": tuple(int(v) for v in stats[i, :4]),
                        "offset": (float(y - cy), float(x - cx))})
    return sorted(objects, key=lambda o: o["area"], reverse=True)


# --------------------------------------------------------------------------- #
# camera <-> stage                                                             #
# --------------------------------------------------------------------------- #
class StageCameraCalibration:
    """Linear map between stage moves (µm) and image content shifts (px).

    `A` is 2x2 with columns = content shift (dy, dx) per µm of +X and of +Y
    stage travel. Measuring it on the frames you actually process absorbs
    camera rotation, flips and axis signs, so a closed loop cannot run the
    wrong way.
    """

    def __init__(self, A, details=None):
        self.A = np.asarray(A, dtype=float).reshape(2, 2)
        if abs(np.linalg.det(self.A)) < 1e-12:
            raise ValueError("calibration matrix is singular - X and Y moves gave parallel shifts")
        self.details = details or {}

    @classmethod
    def measure(cls, snap, move_relative, step_um, settle_s=0.3, min_confidence=0.05):
        """Move +X, back, +Y, back by `step_um` and correlate the frames.

        `snap()` returns a frame, `move_relative(dx_um, dy_um)` must block until
        the move is done. Pick `step_um` so the content shifts by roughly
        10-30 % of the frame. The stage ends where it started.
        """
        def frame():
            time.sleep(settle_s)
            return snap()

        ref = frame()
        shifts, confidences = [], []
        for dx, dy in ((step_um, 0.0), (0.0, step_um)):
            move_relative(dx, dy)
            try:
                sy, sx, conf = phase_correlate(ref, frame())
            finally:
                move_relative(-dx, -dy)
            shifts.append((sy, sx))
            confidences.append(conf)
        ry, rx, rconf = phase_correlate(ref, frame())   # back at the start

        if min(confidences) < min_confidence:
            raise RuntimeError(f"calibration frames did not correlate (peak {min(confidences):.3f}); "
                               "use a structured sample, a smaller step or a longer settle time")
        moved_px = [np.hypot(*s) for s in shifts]
        if min(moved_px) < 2:
            raise RuntimeError(f"image moved only {min(moved_px):.1f} px for {step_um} µm - "
                               "increase step_um")
        A = np.column_stack([np.array(shifts[0]) / step_um, np.array(shifts[1]) / step_um])
        details = {"step_um": step_um, "shift_x_px": shifts[0], "shift_y_px": shifts[1],
                   "confidence": confidences, "return_error_px": (ry, rx),
                   "frame_shape": list(np.asarray(ref).shape[:2])}
        return cls(A, details)

    @property
    def pixel_size_um(self):
        """Mean µm per pixel along the two stage axes"""
        return float(np.mean(1.0 / np.linalg.norm(self.A, axis=0)))

    @property
    def rotation_deg(self):
        """Angle of the stage X axis in the image (0 = +X moves content along +col)"""
        dy, dx = self.A[:, 0]
        return float(np.degrees(np.arctan2(dy, dx)))

    def content_shift(self, dx_um, dy_um):
        """Image content shift (dy, dx) px caused by a stage move"""
        return tuple(self.A @ np.array([dx_um, dy_um]))

    def move_to_center(self, dy_px, dx_px):
        """Stage move (dx_um, dy_um) that brings the image point at offset
        (dy_px, dx_px) from the frame centre into the centre."""
        u = np.linalg.solve(self.A, -np.array([dy_px, dx_px], dtype=float))
        return float(u[0]), float(u[1])

    def stage_offset_of_pixel(self, dy_px, dx_px):
        """Where an image point lies relative to the current stage position, in
        µm: the stage position at which it would sit in the frame centre."""
        return self.move_to_center(dy_px, dx_px)

    def to_dict(self):
        return {"A": self.A.tolist(), "pixel_size_um": self.pixel_size_um,
                "rotation_deg": self.rotation_deg, "details": self.details}

    @classmethod
    def from_dict(cls, d):
        return cls(d["A"], d.get("details"))

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=float)

    @classmethod
    def load(cls, path):
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def __repr__(self):
        return (f"StageCameraCalibration(pixel_size={self.pixel_size_um:.3f} µm/px, "
                f"rotation={self.rotation_deg:.1f}°, det={np.linalg.det(self.A):+.4f})")


class SafetyBox:
    """Square of half-width `half_width_um` around (x0, y0) that closed-loop
    moves may not leave, plus a cap on the length of a single move."""

    def __init__(self, x0, y0, half_width_um, max_step_um):
        self.x0, self.y0 = float(x0), float(y0)
        self.half_width_um, self.max_step_um = float(half_width_um), float(max_step_um)

    def contains(self, x, y):
        return abs(x - self.x0) <= self.half_width_um and abs(y - self.y0) <= self.half_width_um

    def limit(self, x, y, dx, dy):
        """Clip a relative move (dx, dy) from (x, y): first to `max_step_um`,
        then so the target stays inside the box. Returns (dx, dy, clipped)."""
        length = np.hypot(dx, dy)
        clipped = False
        if length > self.max_step_um:
            dx, dy = dx * self.max_step_um / length, dy * self.max_step_um / length
            clipped = True
        tx = np.clip(x + dx, self.x0 - self.half_width_um, self.x0 + self.half_width_um)
        ty = np.clip(y + dy, self.y0 - self.half_width_um, self.y0 + self.half_width_um)
        if tx != x + dx or ty != y + dy:
            clipped = True
        return float(tx - x), float(ty - y), clipped


class Mosaic:
    """Frames placed by their stage positions (translation only, no blending
    beyond averaging the overlaps). Good for a quick overview of where a
    closed loop went; use a proper stitcher (ASHLAR) for publication images.

    The canvas is in the camera orientation of the frames. `pixel_of_stage`
    maps a stage position to the canvas pixel that is in the frame centre
    when the stage is there.
    """

    def __init__(self, frames, positions, calibration, downsample=1):
        if not frames:
            raise ValueError("no frames")
        self.calibration, self.downsample = calibration, max(1, int(downsample))
        self.p0 = np.asarray(positions[0], dtype=float)
        ds = self.downsample
        small = [to_gray(f)[::ds, ::ds] for f in frames]
        h, w = small[0].shape
        # frame i sees the content of frame 0 shifted by A (p_i - p0), so it
        # belongs at -A (p_i - p0) on a canvas in frame-0 pixel coordinates
        tops = [-np.array(calibration.content_shift(*(np.asarray(p, float) - self.p0))) / ds
                for p in positions]
        tops = np.round(np.array(tops)).astype(int)
        lo = tops.min(axis=0)
        hi = tops.max(axis=0) + (h, w)
        self.origin = -lo                       # canvas pixel of frame 0's top-left corner
        acc = np.zeros(tuple(hi - lo), np.float32)
        weight = np.zeros_like(acc)
        for frame, (ty, tx) in zip(small, tops - lo):
            fh, fw = frame.shape
            acc[ty:ty + fh, tx:tx + fw] += frame
            weight[ty:ty + fh, tx:tx + fw] += 1
        self.image = np.where(weight > 0, acc / np.maximum(weight, 1), np.nan)
        self._centre = np.array([(h * ds - 1) / 2, (w * ds - 1) / 2])

    def pixel_of_stage(self, x, y):
        """(row, col) on the canvas of the point centred at stage position (x, y)"""
        shift = np.array(self.calibration.content_shift(*(self.p0 - (x, y))))
        return tuple((self._centre + shift) / self.downsample + self.origin)

    def show(self, ax, **kwargs):
        """imshow with a robust contrast window; empty canvas stays blank"""
        finite = self.image[np.isfinite(self.image)]
        lo, hi = np.percentile(finite, (1, 99.5)) if finite.size else (0, 1)
        ax.imshow(self.image, cmap=kwargs.pop("cmap", "gray"), vmin=lo, vmax=hi, **kwargs)
        ax.set_axis_off()


# --------------------------------------------------------------------------- #
# client glue                                                                  #
# --------------------------------------------------------------------------- #
def make_snap(client, resize_factor=1):
    """Callable returning the current frame as float32 grayscale"""
    def snap():
        return to_gray(client.recordingManager.snapNumpyToFastAPI(resizeFactor=resize_factor))
    return snap


def make_relative_mover(client, positioner_name=None, speed=5000):
    """Callable `move(dx_um, dy_um)` doing a blocking relative XY move"""
    def move(dx_um, dy_um):
        client.positionersManager.moveRelativeXY(dx_um, dy_um, positioner_name=positioner_name,
                                                 speed=speed)
    return move


def get_xy(client, positioner_name=None):
    """Current (X, Y) in µm, user frame"""
    positions = client.positionersManager.getPositionerPositions()
    pos = positions[positioner_name] if positioner_name else next(iter(positions.values()))
    return float(pos["X"]), float(pos["Y"])
