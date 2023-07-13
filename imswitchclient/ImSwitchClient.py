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
        self.get_json(self.base_uri+"/openapi.json")
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        
    @property
    def base_uri(self):
        return f"http://{self.host}:{self.port}"

    def get_json(self, path, payload={}, headers={}):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path, params=payload, headers=headers)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}, headers={}, wait_on_task="auto"):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.post(path, json=payload, headers=headers)
        r.raise_for_status()
        r = r.json()
        return r

    def move_positioner(self, positioner_name, axis, dist, is_absolute=True, is_blocking=True):
        url = f"{self.base_uri}/PositionerController/movePositioner"
        payload = {
            'positionerName': positioner_name,
            'axis': axis,
            'dist': dist,
            'isAbsolute': is_absolute,
            'isBlocking': is_blocking
        }
        #headers = {'accept': 'application/json'}

        response = self.get_json(url, payload=payload)
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
    


def task_href(t):
    """Extract the endpoint address from a task dictionary"""
    return t["links"]["self"]["href"]

def is_a_task(t):
    """Return true if a parsed JSON return value represents a task"""
    self_href = task_href(t)
    try:
        return ("/api/v2/tasks/" in self_href or "/api/v2/actions/" in self_href)
    except:
        return False

def poll_task(task):
    """Poll a task until it finishes, and return the return value"""
    assert is_a_task(task), ("poll_task must be called with a "
                "parsed JSON representation of a task")
    log_n = 0
    while task["status"] in ACTION_RUNNING_KEYWORDS:
        r = requests.get(task_href(task))
        r.raise_for_status()
        task = r.json()
        while len(task["log"]) > log_n:
            d = task["log"][log_n]
            logging.log(d["levelno"], d["message"])
            log_n += 1
    for output_key in ACTION_OUTPUT_KEYS:
        if output_key in task:
            return task[output_key]
    return None
