import requests
import json
import time
import io
import PIL.Image
import numpy as np
import logging
import os

from .positionersManager import positionersManager
from .recordingManager import recordingManager


class ImSwitchClient(object):
    def __init__(self, host="localhost", port=8000):
        self.host = host
        self.port = port
        self.get_json(self.base_uri+"/openapi.json")
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        
        # register managers
        self.positionersManager = positionersManager(self)
        self.recordingManager = recordingManager(self)
        
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


