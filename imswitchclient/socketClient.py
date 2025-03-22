import socketio
import logging
import ssl

class socketClient(object):
    def __init__(self, host="localhost", port=8002, isHttps=False):
        self.host = host
        self.port = port
        self.isHttps = isHttps
        self.images = []  # list to store received image messages
        self.image_callback = None  # optional callback for image updates
        self.sio = socketio.Client(ssl_verify=False)
        self.sio.on("sigUpdateImage", self._on_sig_update_image)
        self.sio.on("sigExperimentImageUpdate", self._on_sig_experiment_image_update)
        self.connect()

    def connect(self):
        if self.isHttps:
            url = f"https://{self.host}:{self.port}"
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            logging.info(f"Connecting securely (no cert check) to {url}")
            
            self.sio.connect(url)

        else:
            url = f"http://{self.host}:{self.port}"
            logging.info(f"Connecting to {url}")
            self.sio.connect(url)

    def _on_sig_update_image(self, data):
        self.images.append(data)
        if self.image_callback:
            self.image_callback(data)

    def _on_sig_experiment_image_update(self, data):
        self.images.append(data)
        if self.image_callback:
            self.image_callback(data)
    
    def get_images(self):
        return self.images

    def set_image_callback(self, callback):
        self.image_callback = callback