class ledMatrixManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def setAllLED(self, state, intensity):
        """Set all LEDs with specified state and intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLED"
        payload = {
            'state': state,
            'intensity': intensity
        }
        response = self.parent.get_json(url, payload=payload)
        return response
    
    def setAllLEDOff(self):
        """Turn off all LEDs"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLEDOff"
        response = self.parent.get_json(url)
        return response

    def setAllLEDOn(self):
        """Turn on all LEDs"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLEDOn"
        response = self.parent.get_json(url)
        return response

    def setIntensity(self, intensity):
        """Set LED intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setIntensity"
        payload = {
            'intensity': intensity
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setLED(self, led_id, state):
        """Set a specific LED with given ID and state"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setLED"
        payload = {
            'LEDid': led_id,
            'state': state
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setSpecial(self, pattern, intensity, get_return=False):
        """Set special LED pattern with intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setSpecial"
        payload = {
            'pattern': pattern,
            'intensity': intensity,
            'getReturn': get_return
        }
        response = self.parent.get_json(url, payload=payload)
        return response