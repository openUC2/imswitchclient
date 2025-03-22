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
from .lasersManager import lasersManager
from .histoscanManager import histoscanManager
from .objectiveController import objectiveController
from .socketClient import socketClient

class ImSwitchClient(object):
    def __init__(self, host="0.0.0.0", isHttps=True, port=8001, socket_port=8002):
        self.host = host
        self.port = port
        self.isHttps = isHttps
        self.get_json(self.base_uri+"/openapi.json")
        
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        
        # register managers
        self.positionersManager = positionersManager(self)
        self.recordingManager = recordingManager(self)
        self.lasersManager = lasersManager(self)
        self.histoscanManager = histoscanManager(self)
        self.objectiveController = objectiveController(self)

        # initialize Socket.IO client
        self.socketClient = socketClient(host=self.host, port=socket_port, isHttps=self.isHttps)

        
    @property
    def base_uri(self):
        if self.isHttps:
            return f"https://{self.host}:{self.port}"
        else:
            return f"http://{self.host}:{self.port}"

    def get_json(self, path, payload={}, headers={}):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path, params=payload, headers=headers, verify=False)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}, headers={}, wait_on_task="auto"):
        """Make an HTTP POST request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.post(path, json=payload, headers=headers, verify=False)
        r.raise_for_status()
        r = r.json()
        return r


