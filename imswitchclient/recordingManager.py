
import requests
import json
import numpy as np
import PIL
import io
import cv2
import threading
import time
import enum
import base64
import PIL.Image

class SaveFormat(enum.Enum):
    TIFF = 1
    HDF5 = 2
    ZARR = 3
    MP4 = 4
    PNG = 5
    JPG = 6
    OME_TIFF = 7
    OME_ZARR = 8
    STITCHED_TIFF = 9

def _formatValue(save_format):
    return save_format.value if isinstance(save_format, SaveFormat) else int(save_format)


class MJPEGStreamReceiver:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.frame = None
        self.streaming = False
        self.thread = None
        self.lock = threading.Lock()

    def startStream(self):
        if not self.streaming:
            self.streaming = True
            self.thread = threading.Thread(target=self._pull_frames, daemon=True)
            self.thread.start()

    def _pull_frames(self):
        # Continuously pull frames from the MJPEG stream
        with requests.get(self.stream_url, stream=True, verify=False) as response:
            if response.status_code == 200:
                bytes_stream = bytes()
                for chunk in response.iter_content(chunk_size=1024):
                    bytes_stream += chunk
                    a = bytes_stream.find(b'\xff\xd8')  # Start of JPEG
                    b = bytes_stream.find(b'\xff\xd9')  # End of JPEG
                    if a != -1 and b != -1:
                        jpg_data = bytes_stream[a:b+2]
                        bytes_stream = bytes_stream[b+2:]

                        # Decode the image and store it
                        image = cv2.imdecode(np.frombuffer(jpg_data, np.uint8), cv2.IMREAD_COLOR)
                        if image is not None:
                            with self.lock:
                                self.frame = image

    def stopStream(self):
        if self.streaming:
            self.streaming = False
            self.thread.join()

    def getFrame(self) -> np.ndarray:
        # Retrieve the most recent frame
        with self.lock:
            if self.frame is not None:
                return self.frame.copy()  # Return a copy to avoid race conditions
            else:
                return None

if __name__ == "__main__":
    # Example usage with FastAPI
    stream_url = "https://localhost:8001/RecordingController/video_feeder"
    mjpeg_receiver = MJPEGStreamReceiver(stream_url)
    mjpeg_receiver.startStream()
    time.sleep(1)
    frame = mjpeg_receiver.getFrame()
    mjpeg_receiver.stopStream()



class recordingManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        self.videoStream = MJPEGStreamReceiver(f"{self.parent.base_uri}/RecordingController/video_feeder")    
        
    def snapNumpyToFastAPI(self, resizeFactor=1):        
        url = f"{self.parent.base_uri}/RecordingController/snapNumpyToFastAPI"
        headers = {'accept': 'application/json'}
        payload ={'resizeFactor':resizeFactor}
        # we do not use parent's get function here
        response = requests.get(url, params=payload, headers=headers, verify=False)
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        if content_type == 'image/png':
            image_data = response.content
            image = PIL.Image.open(io.BytesIO(image_data))
            return np.array(image)
        else:
            raise ValueError("Unexpected response content-type. Expected 'image/png'.")
        
    def startVideoStream(self):
        '''
        Start pulling frames from the MJPEG stream
        '''
        self.videoStream.startStream()
        
    def stopVideoStream(self):
        '''
        Stop pulling frames from the MJPEG stream
        '''
        self.videoStream.stopStream()
        
    def getVideoFrame(self):
        '''
        Get the most recent frame from the MJPEG stream
        '''
        return self.videoStream.getFrame()
    
    def startRecording(self, save_format=None):
        """Start recording with optional save format"""
        url = f"{self.parent.base_uri}/RecordingController/startRecording"
        headers = {'accept': 'application/json'}
        payload = {}
        if save_format is not None:
            if isinstance(save_format, SaveFormat):
                payload['saveFormat'] = save_format.value
            else:
                payload['saveFormat'] = save_format
        response = self.parent.get_json(url, payload=payload, headers=headers)
        return response
    
    def stopRecording(self):
        """Stop current recording"""
        url = f"{self.parent.base_uri}/RecordingController/stopRecording"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        return response
    
    def snapImageToPath(self, file_name, save_format=SaveFormat.TIFF, return_preview=False,
                        preview_max_size=1024, timeout=30):
        """Snap image and save to specified path.

        Blocks for the whole exposure - use `snapAndWait` for exposures longer
        than `timeout` seconds.
        """
        url = f"{self.parent.base_uri}/RecordingController/snapImageToPath"
        headers = {'accept': 'application/json'}
        payload = {'fileName': file_name, 'saveFormat': _formatValue(save_format),
                   'returnPreview': return_preview, 'previewMaxSize': preview_max_size}
        response = self.parent.get_json(url, payload=payload, headers=headers, timeout=timeout)
        return response

    # --- background snaps (long exposures) ---------------------------------
    def startSnap(self, file_name=None, save_format=SaveFormat.TIFF, return_preview=True,
                  preview_max_size=1024):
        """Start a snap on the server and return at once with its `jobId`.

        The server arms the camera, waits one full fresh exposure, writes the
        file under `<dataRoot>/recordings/<date>/` and keeps the result for
        `getSnapStatus`.
        """
        url = f"{self.parent.base_uri}/RecordingController/startSnap"
        payload = {'saveFormat': _formatValue(save_format), 'returnPreview': return_preview,
                   'previewMaxSize': preview_max_size}
        if file_name is not None:
            payload['fileName'] = file_name
        return self.parent.get_json(url, payload=payload)

    def getSnapStatus(self, job_id=None):
        """status (pending/running/done/error/cancelled), progress 0-100, result once done"""
        url = f"{self.parent.base_uri}/RecordingController/getSnapStatus"
        payload = {} if job_id is None else {'jobId': job_id}
        return self.parent.get_json(url, payload=payload)

    def cancelSnap(self, job_id=None):
        """Abort a running snap; stops the exposure in the camera driver"""
        url = f"{self.parent.base_uri}/RecordingController/cancelSnap"
        payload = {} if job_id is None else {'jobId': job_id}
        return self.parent.get_json(url, payload=payload)

    def snapAndWait(self, file_name=None, save_format=SaveFormat.TIFF, return_preview=True,
                    preview_max_size=1024, poll=5.0, timeout=None, on_progress=None,
                    stop_event=None):
        """`startSnap` + poll until the job finishes; returns the snap result dict.

        The result has `fullPath`, `relativeFilePath` (use with `downloadImage`)
        and, with `return_preview`, a `previewImage` PNG data URL (decode with
        `previewToNumpy`). `timeout` in seconds, None waits forever. Interrupting
        the cell (KeyboardInterrupt), setting the `threading.Event` `stop_event`
        or hitting the timeout cancels the exposure on the server instead of
        leaving it running.
        """
        job = self.startSnap(file_name, save_format, return_preview, preview_max_size)
        job_id = job.get('jobId')
        t0 = time.time()
        try:
            while True:
                status = self.getSnapStatus(job_id)
                if on_progress:
                    on_progress(status)
                state = status.get('status')
                if state == 'done':
                    return status.get('result') or {}
                if state in ('error', 'cancelled', 'unknown'):
                    raise RuntimeError(f"Snap {job_id} {state}: {status.get('error', '')}")
                if timeout is not None and time.time() - t0 > timeout:
                    raise TimeoutError(f"Snap {job_id} exceeded {timeout} s")
                if stop_event is not None:
                    if stop_event.wait(poll):
                        raise InterruptedError(f"Snap {job_id} stopped")
                else:
                    time.sleep(poll)
        except (KeyboardInterrupt, TimeoutError, InterruptedError):
            self.cancelSnap(job_id)
            raise

    @staticmethod
    def previewToNumpy(result):
        """Decode the `previewImage` data URL of a snap result into an 8-bit array"""
        data_url = (result or {}).get('previewImage')
        if not data_url:
            return None
        return np.array(PIL.Image.open(io.BytesIO(base64.b64decode(data_url.split(',', 1)[-1]))))

    def dataUrl(self, relative_file_path):
        """URL of a file below the server's data folder (as `relativeFilePath` reports it)"""
        return f"{self.parent.base_root_uri}/data/{relative_file_path.lstrip('/')}"

    def downloadFile(self, relative_file_path, target_path=None, timeout=300):
        """Download a file from the server's data folder; returns the bytes,
        or `target_path` after writing them there."""
        response = requests.get(self.dataUrl(relative_file_path), verify=False, timeout=timeout)
        response.raise_for_status()
        if target_path is None:
            return response.content
        with open(target_path, 'wb') as f:
            f.write(response.content)
        return target_path

    def downloadImage(self, relative_file_path, timeout=300):
        """Download a snapped image at full bit depth as a numpy array.

        Uses `tifffile` when installed (keeps 16-bit and multi-page TIFFs),
        Pillow otherwise.
        """
        content = self.downloadFile(relative_file_path, timeout=timeout)
        try:
            import tifffile
            if relative_file_path.lower().endswith(('.tif', '.tiff')):
                return tifffile.imread(io.BytesIO(content))
        except ImportError:
            pass
        return np.array(PIL.Image.open(io.BytesIO(content)))
