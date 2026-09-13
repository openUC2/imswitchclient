import os
import requests
import logging
from urllib.parse import urlsplit
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

DEFAULT_ROUTE = "/imswitch/api"
DEFAULT_PORT = 8001


def parseBaseUrl(url, defaultRoute=DEFAULT_ROUTE):
    """Split a base URL into (host, port, isHttps, route).

    Takes whatever you can copy out of the browser's address bar::

        http://192.168.178.76/imswitch/api/docs -> ('192.168.178.76', 80, False, '/imswitch/api')
        http://100.100.43.118:8001             -> ('100.100.43.118', 8001, False, '/imswitch/api')
        https://imswitch.openuc2.com           -> ('imswitch.openuc2.com', 443, True, '/imswitch/api')
    """
    parts = urlsplit(url if "://" in url else f"http://{url}")
    isHttps = parts.scheme == "https"
    route = parts.path.rstrip("/")
    for suffix in ("/docs", "/redoc", "/openapi.json"):
        if route.endswith(suffix):
            route = route[: -len(suffix)]
    port = parts.port or (443 if isHttps else 80)
    return parts.hostname, port, isHttps, route or defaultRoute


class ImSwitchClient(object):
    def __init__(self, host=None, isHttps=None, port=None, route=None, socket_port=None):
        """Connect to an ImSwitch server.

        `host` may be a full URL, which is the least error-prone way to reach a
        server that is not on the default port::

            ImSwitchClient("http://192.168.178.76/imswitch/api")  # Docker/Caddy on port 80
            ImSwitchClient("http://100.100.43.118:8001")          # local instance
            ImSwitchClient("imswitch.openuc2.com")                # host only -> port 8001
            ImSwitchClient()                                      # $IMSWITCH_API_URL, else localhost:8001

        A plain host name keeps the historical defaults (port 8001, http). A URL
        without a port uses the scheme's port (80/443). Explicit `isHttps`,
        `port` and `route` arguments always win over what the URL says.
        `socket_port` defaults to the API port - set it when Socket.IO is not
        proxied on the same port.
        """
        url = host if (host and "://" in host) else None
        if url is None and host is None:
            url = os.environ.get("IMSWITCH_API_URL") or None
        if url:
            urlHost, urlPort, urlHttps, urlRoute = parseBaseUrl(url)
        else:
            urlHost, urlPort, urlHttps, urlRoute = host, None, None, None

        self.host = urlHost or "localhost"
        self.isHttps = isHttps if isHttps is not None else bool(urlHttps)
        self.port = port if port is not None else (urlPort or (443 if self.isHttps else DEFAULT_PORT))
        self.route = (route or urlRoute or DEFAULT_ROUTE).rstrip("/")
        self.get_json(self.base_swagger_uri)

        logging.info(f"Connecting to microscope at {self.base_uri}")
        
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
            self.socketClient = socketClient(host=self.host,
                                             port=socket_port or self.port,
                                             isHttps=self.isHttps)
        except Exception as e:
            logging.error(f"Failed to connect Socket.IO client: {e}")
            self.socketClient = None
        
    @property
    def base_uri(self):
        scheme = "https" if self.isHttps else "http"
        return f"{scheme}://{self.host}:{self.port}{self.route}"

    @property
    def base_root_uri(self):
        """Server root without the API suffix - serves /data, /jupyter, /openapi.json"""
        base = self.base_uri
        return base[:-4] if base.endswith("/api") else base

    @property
    def base_swagger_uri(self):
        return self.base_root_uri + "/openapi.json"
        
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


