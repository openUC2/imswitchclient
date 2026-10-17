#!/usr/bin/env python
"""Tests for `imswitchclient.smart` on a simulated microscope.

`FakeScope` crops a frame out of a large random texture at the stage
position, through a camera that is rotated and mirrored relative to the
stage, so the calibration has to recover orientation as well as scale.
Runs with pytest or standalone: `python tests/test_smart.py`.
"""

import os
import sys
import unittest

import cv2
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from imswitchclient import smart  # noqa: E402


def texture(size=1200, seed=0):
    rng = np.random.default_rng(seed)
    return cv2.GaussianBlur(rng.random((size, size)).astype(np.float32), (0, 0), 2.0) + 1.0


class FakeScope:
    """Stage in µm, camera with `um_per_px`, rotated by `angle_deg` and
    optionally mirrored. The world texture has 1 µm pixels."""

    def __init__(self, um_per_px=2.0, angle_deg=30.0, mirror=True, shape=(120, 160)):
        self.world = texture()
        self.x = self.y = 0.0
        self.um_per_px, self.shape = um_per_px, shape
        a = np.radians(angle_deg)
        rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
        flip = np.diag([1.0, -1.0]) if mirror else np.eye(2)
        # camera (col, row) offset from frame centre, px -> world (x, y) offset, µm
        self.cam_to_world = um_per_px * rot @ flip

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def snap(self):
        h, w = self.shape
        rows, cols = np.mgrid[0:h, 0:w].astype(np.float32)
        cam = np.stack([cols - (w - 1) / 2, rows - (h - 1) / 2])            # (2, h, w)
        world = np.tensordot(self.cam_to_world, cam, axes=1)
        cx, cy = self.world.shape[1] / 2, self.world.shape[0] / 2
        map_x = (world[0] + cx + self.x).astype(np.float32)
        map_y = (world[1] + cy + self.y).astype(np.float32)
        return cv2.remap(self.world, map_x, map_y, cv2.INTER_LINEAR)

    def pixel_of_world(self, wx, wy):
        """(dy, dx) offset from the frame centre at which world point (wx, wy) µm appears"""
        col, row = np.linalg.solve(self.cam_to_world, [wx - self.x, wy - self.y])
        return row, col


class TestPhaseCorrelate(unittest.TestCase):
    def test_recovers_integer_and_subpixel_shift(self):
        img = texture(256)[:128, :160]
        moved = np.roll(img, (7, -12), axis=(0, 1))
        dy, dx, conf = smart.phase_correlate(img, moved)
        self.assertAlmostEqual(dy, 7, delta=0.2)
        self.assertAlmostEqual(dx, -12, delta=0.2)
        self.assertGreater(conf, 0.15)

        M = np.float32([[1, 0, 3.5], [0, 1, -2.25]])
        sub = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)
        dy, dx, _ = smart.phase_correlate(img, sub)
        self.assertAlmostEqual(dy, -2.25, delta=0.3)
        self.assertAlmostEqual(dx, 3.5, delta=0.3)

    def test_unrelated_frames_have_low_confidence(self):
        _, _, conf = smart.phase_correlate(texture(seed=1)[:128, :128], texture(seed=2)[:128, :128])
        self.assertLess(conf, 0.05)


class TestCalibration(unittest.TestCase):
    def setUp(self):
        self.scope = FakeScope()
        self.cal = smart.StageCameraCalibration.measure(self.scope.snap, self.scope.move,
                                                        step_um=40, settle_s=0)

    def test_scale_and_return_to_start(self):
        self.assertAlmostEqual(self.cal.pixel_size_um, 2.0, delta=0.05)
        self.assertEqual((self.scope.x, self.scope.y), (0.0, 0.0))

    def test_move_to_center_centres_a_point(self):
        dy, dx = self.scope.pixel_of_world(60.0, -35.0)
        mx, my = self.cal.move_to_center(dy, dx)
        self.scope.move(mx, my)
        dy2, dx2 = self.scope.pixel_of_world(60.0, -35.0)
        self.assertLess(np.hypot(dy2, dx2), 0.5)

    def test_round_trip_through_dict(self):
        again = smart.StageCameraCalibration.from_dict(self.cal.to_dict())
        np.testing.assert_allclose(again.A, self.cal.A)

    def test_featureless_sample_is_rejected(self):
        scope = FakeScope()
        scope.world = np.ones_like(scope.world)
        with self.assertRaises(RuntimeError):
            smart.StageCameraCalibration.measure(scope.snap, scope.move, step_um=40, settle_s=0)


class TestMosaic(unittest.TestCase):
    def test_frames_line_up_and_stage_points_map(self):
        scope = FakeScope(um_per_px=1.0, angle_deg=0, mirror=False)
        cal = smart.StageCameraCalibration.measure(scope.snap, scope.move, step_um=30, settle_s=0)
        frames, positions = [], []
        for x, y in ((0, 0), (100, 0), (100, 60)):
            scope.x, scope.y = x, y
            frames.append(scope.snap())
            positions.append((x, y))
        m = smart.Mosaic(frames, positions, cal)
        # overlapping frames agree, so the average equals frame 0 where it lies
        r0, c0 = m.origin
        np.testing.assert_allclose(m.image[r0:r0 + 120, c0:c0 + 160], frames[0], atol=0.02)
        # the centre of the last frame is where its stage position maps to
        r, c = (int(round(v)) for v in m.pixel_of_stage(100, 60))
        self.assertAlmostEqual(m.image[r, c], frames[2][60, 80], delta=0.05)


class TestSafetyBox(unittest.TestCase):
    def test_step_cap_and_box(self):
        box = smart.SafetyBox(0, 0, half_width_um=100, max_step_um=50)
        self.assertEqual(box.limit(0, 0, 30, 40), (30.0, 40.0, False))
        dx, dy, clipped = box.limit(0, 0, 300, 400)
        self.assertTrue(clipped)
        self.assertAlmostEqual(np.hypot(dx, dy), 50)
        dx, dy, clipped = box.limit(90, 0, 40, 0)
        self.assertEqual((dx, clipped), (10.0, True))
        self.assertFalse(box.contains(101, 0))


class TestDetection(unittest.TestCase):
    def test_find_objects_and_offset(self):
        rng = np.random.default_rng(3)
        img = rng.normal(100, 2, (120, 160)).astype(np.float32)
        cv2.circle(img, (130, 30), 6, 160, -1)
        cv2.circle(img, (40, 90), 3, 160, -1)
        objs = smart.find_objects(img, min_area=10)
        self.assertEqual(len(objs), 2)
        self.assertAlmostEqual(objs[0]["x"], 130, delta=0.5)
        self.assertAlmostEqual(objs[0]["offset"][0], 30 - 59.5, delta=0.5)

    def test_dark_objects(self):
        img = np.full((100, 100), 200, np.float32) + np.random.default_rng(4).normal(0, 2, (100, 100))
        cv2.circle(img, (50, 50), 8, 50, -1)
        self.assertEqual(len(smart.find_objects(img, dark_objects=True)), 1)
        self.assertEqual(len(smart.find_objects(img)), 0)


class TestEmptyFieldReference(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(6)
        self.shape = (150, 200)

    def dark(self):
        return np.abs(self.rng.normal(0, 2, self.shape)).round().astype(np.float32)

    def test_dark_field(self):
        ref = smart.EmptyFieldReference(self.dark())
        specks = self.dark()                     # empty glass with a little dust
        for y, x in self.rng.integers(10, 140, (8, 2)):
            cv2.circle(specks, (int(x), int(y)), 1, 255, -1)
        tissue = self.dark() + 120 * texture(256)[:150, :200]
        half = self.dark()
        half[:, 100:] = tissue[:, 100:]
        self.assertLess(ref.coverage(self.dark()), 0.01)
        self.assertLess(ref.coverage(specks), 0.05)
        self.assertGreater(ref.coverage(tissue), 0.9)
        self.assertAlmostEqual(ref.coverage(half), 0.5, delta=0.1)

    def test_brightfield_with_vignetting(self):
        yy, xx = np.mgrid[0:150, 0:200]
        vignetting = 4000 * (1 - 0.3 * (((yy - 75) / 75) ** 2 + ((xx - 100) / 100) ** 2))

        def frame(absorption=0.0):
            return self.rng.poisson(vignetting * (1 - absorption)).astype(np.float32)

        ref = smart.EmptyFieldReference([frame(), frame()])
        cells = 0.3 * (texture(256)[:150, :200] > 1.55)
        self.assertLess(ref.coverage(frame()), 0.01)
        self.assertGreater(ref.coverage(frame(cells)), 0.5 * cells.astype(bool).mean())
        self.assertAlmostEqual(ref.coverage(frame(np.where(xx >= 100, 0.3, 0.0))), 0.5, delta=0.05)

    def test_textured_empty_background_moves_with_the_stage(self):
        # Faint structure in the glass/medium is part of the sample plane, so it
        # is shifted between the reference and every later tile. It must not
        # count as sample; real sample with clear contrast must.
        t = texture(400, seed=9)
        world = 5 * (t > np.percentile(t, 85)).astype(np.float32)   # 15 % faint specks

        def view(y, x, extra=0.0):
            return self.dark() + world[y:y + 150, x:x + 200] + extra

        ref = smart.EmptyFieldReference(view(0, 0))
        self.assertLess(ref.coverage(view(120, 170)), 0.05)
        sample = 60 * (texture(256, seed=3)[:150, :200] > 1.5)
        self.assertGreater(ref.coverage(view(120, 170, sample)), 0.5 * (sample > 0).mean())

    def test_shape_mismatch(self):
        ref = smart.EmptyFieldReference(self.dark())
        with self.assertRaises(ValueError):
            ref.coverage(np.zeros((10, 10), np.float32))


if __name__ == "__main__":
    unittest.main()
