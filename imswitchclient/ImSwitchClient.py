import requests
import logging
from .positionersManager import positionersManager
from .recordingManager import recordingManager
from .lasersManager import lasersManager
from .histoscanManager import histoscanManager
from .experimentController import ExperimentController
from .mdaController import mdaController
from .objectiveController import objectiveController
from .ledMatrixManager import ledMatrixManager
from .settingsManager import settingsManager
from .readnoiseManager import readnoiseManager
from .viewManager import viewManager
from .communicationManager import communicationManager
from .socketClient import socketClient

class ImSwitchClient(object):
    def __init__(self, host="0.0.0.0", isHttps=False, port=8001, route="/imswitch/api"):
        self.host = host
        self.port = port
        self.isHttps = isHttps
        self.route = route
        self.get_json(self.base_swagger_uri)
        
        logging.info(f"Connecting to microscope {self.host}:{self.port}")
        
        # register managers
        self.positionersManager = positionersManager(self)
        self.recordingManager = recordingManager(self)
        self.lasersManager = lasersManager(self)
        self.histoscanManager = histoscanManager(self)
        self.experimentController = ExperimentController(self)
        self.mdaController = mdaController(self)
        self.objectiveController = objectiveController(self)
        self.ledMatrixManager = ledMatrixManager(self)
        self.settingsManager = settingsManager(self)
        self.readnoiseManager = readnoiseManager(self)
        self.viewManager = viewManager(self)
        self.communicationManager = communicationManager(self)

        # initialize Socket.IO client
        try:
            self.socketClient = socketClient(host=self.host, port=port, isHttps=self.isHttps)
        except Exception as e:
            logging.error(f"Failed to connect Socket.IO client: {e}")
            self.socketClient = None
        
    @property
    def base_uri(self):
        if self.isHttps:
            return f"https://{self.host}:{self.port}{self.route}"
        else:
            return f"http://{self.host}:{self.port}{self.route}"

    @property
    def base_swagger_uri(self):
        return self.base_uri.replace("/api", "") + "/openapi.json"
        
    def get_json(self, path, payload={}, headers={}, timeout=30):
        """Perform an HTTP GET request and return the JSON response"""
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.get(path, params=payload, headers=headers, verify=False, timeout=timeout)
        r.raise_for_status()
        return r.json()

    def post_json(self, path, payload={}, headers={}, wait_on_task="auto", params=None, timeout=30):
        """Make an HTTP POST request and return the JSON response.

        `params` goes into the query string: FastAPI puts scalar arguments of a
        POST endpoint there, only pydantic-model arguments come from the body.
        """
        if not path.startswith("http"):
            path = self.base_uri + path
        r = requests.post(path, json=payload, params=params, headers=headers,
                          verify=False, timeout=timeout)
        r.raise_for_status()
        r = r.json()
        return r


