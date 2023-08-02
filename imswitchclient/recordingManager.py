
import requests
import json
import numpy as np
import PIL
import io

class recordingManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def snapNumpyToFastAPI(self):        
        url = f"{self.parent.base_uri}/RecordingController/snapNumpyToFastAPI"
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
        

