import requests
import json
import time
import io
import PIL.Image
import numpy as np
import logging
import zeroconf
import os


class ImSwitchClient(object):
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.get_json(self.base_uri)
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        
    @property
    def base_uri(self):
        return f"http://{self.host}:{self.port}/api/v2"

    def get_json(self, path):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}, wait_on_task="auto"):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.post(path, json=payload)
        r.raise_for_status()
        r = r.json()
        if wait_on_task == "auto":
            wait_on_task = is_a_task(r)
        if wait_on_task:
            return poll_task(r)
        else:
            return r

    def move_positioner(self, positioner_name, axis, dist, is_absolute=True, is_blocking=True):
        url = f"{self.base_uri}/PositionerController/movePositioner"
        params = {
            'positionerName': positioner_name,
            'axis': axis,
            'dist': dist,
            'isAbsolute': is_absolute,
            'isBlocking': is_blocking
        }
        headers = {'accept': 'application/json'}

        response = self.get_json(url, params=params, headers=headers)
        return response

    def snap_numpy_to_fastapi(self):
        url = f"{self.base_uri}/RecordingController/snapNumpyToFastAPI"
        headers = {'accept': 'application/json'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        if content_type == 'image/png':
            image_data = response.content
            image = PIL.Image.open(io.BytesIO(image_data))
            return np.array(image)
        else:
            raise ValueError("Unexpected response content-type. Expected 'image/png'.")
        
    def get_positioner_names(self):
        url = f"{self.base_uri}/PositionerController/getPositionerNames"
        headers = {'accept': 'application/json'}

        response = self.get_json(url, headers=headers)
        return response