class ledMatrixManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def setAllLED(self, state=None, intensity=None, intensity_r=None, intensity_g=None, intensity_b=None, get_return=True):
        """Set all LEDs with specified state and intensity (optionally per color channel)"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLED"
        payload = {}
        if state is not None:
            payload['state'] = state
        if intensity is not None:
            payload['intensity'] = intensity
        if intensity_r is not None:
            payload['intensity_r'] = intensity_r
        if intensity_g is not None:
            payload['intensity_g'] = intensity_g
        if intensity_b is not None:
            payload['intensity_b'] = intensity_b
        payload['getReturn'] = get_return
        response = self.parent.get_json(url, payload=payload)
        return response
    
    def setAllLEDOff(self, get_return=True):
        """Turn off all LEDs"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLEDOff"
        payload = {'getReturn': get_return}
        response = self.parent.get_json(url, payload=payload)
        return response

    def setAllLEDOn(self, get_return=True):
        """Turn on all LEDs"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setAllLEDOn"
        payload = {'getReturn': get_return}
        response = self.parent.get_json(url, payload=payload)
        return response

    def setCircle(self, circle_radius, intensity, intensity_r=None, intensity_g=None, intensity_b=None):
        """Set circular LED pattern with specified radius and intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setCircle"
        payload = {
            'circleRadius': circle_radius,
            'intensity': intensity
        }
        if intensity_r is not None:
            payload['intensity_r'] = intensity_r
        if intensity_g is not None:
            payload['intensity_g'] = intensity_g
        if intensity_b is not None:
            payload['intensity_b'] = intensity_b
        response = self.parent.get_json(url, payload=payload)
        return response

    def setEnabled(self, enabled):
        """Enable or disable the LED matrix"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setEnabled"
        payload = {'enabled': enabled}
        response = self.parent.get_json(url, payload=payload)
        return response

    def setHalves(self, intensity, direction, intensity_r=None, intensity_g=None, intensity_b=None):
        """Set half of the LED matrix in specified direction"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setHalves"
        payload = {
            'intensity': intensity,
            'direction': direction
        }
        if intensity_r is not None:
            payload['intensity_r'] = intensity_r
        if intensity_g is not None:
            payload['intensity_g'] = intensity_g
        if intensity_b is not None:
            payload['intensity_b'] = intensity_b
        response = self.parent.get_json(url, payload=payload)
        return response

    def setIntensity(self, intensity=None):
        """Set LED intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setIntensity"
        payload = {}
        if intensity is not None:
            payload['intensity'] = intensity
        response = self.parent.get_json(url, payload=payload)
        return response

    def setLED(self, led_id, state=None):
        """Set a specific LED with given ID and state"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setLED"
        payload = {'LEDid': led_id}
        if state is not None:
            payload['state'] = state
        response = self.parent.get_json(url, payload=payload)
        return response

    def setRing(self, ring_radius, intensity, intensity_r=None, intensity_g=None, intensity_b=None):
        """Set ring LED pattern with specified radius and intensity"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setRing"
        payload = {
            'ringRadius': ring_radius,
            'intensity': intensity
        }
        if intensity_r is not None:
            payload['intensity_r'] = intensity_r
        if intensity_g is not None:
            payload['intensity_g'] = intensity_g
        if intensity_b is not None:
            payload['intensity_b'] = intensity_b
        response = self.parent.get_json(url, payload=payload)
        return response

    def setStatus(self, status="idle"):
        """Set the status of the LED matrix"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setStatus"
        payload = {'status': status}
        response = self.parent.get_json(url, payload=payload)
        return response

    def setValue(self, value):
        """Set the value of the LED matrix"""
        url = f"{self.parent.base_uri}/LEDMatrixController/setValue"
        payload = {'value': value}
        response = self.parent.get_json(url, payload=payload)
        return response