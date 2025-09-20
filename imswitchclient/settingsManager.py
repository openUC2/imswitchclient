class settingsManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def getDetectorNames(self):
        """Get all available detector names"""
        url = f"{self.parent.base_uri}/SettingsController/getDetectorNames"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        return response
    
    def setDetectorBinning(self, detector_name, binning):
        """Set detector binning"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorBinning"
        payload = {
            'detectorName': detector_name,
            'binning': binning
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setDetectorExposureTime(self, detector_name, exposure_time):
        """Set detector exposure time"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorExposureTime"
        payload = {
            'detectorName': detector_name,
            'exposureTime': exposure_time
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setDetectorGain(self, detector_name, gain):
        """Set detector gain"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorGain"
        payload = {
            'detectorName': detector_name,
            'gain': gain
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setDetectorParameter(self, detector_name, parameter_name, value):
        """Set a generic detector parameter"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorParameter"
        payload = {
            'detectorName': detector_name,
            'parameterName': parameter_name,
            'value': value
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setDetectorROI(self, detector_name, x=None, y=None, w=None, h=None):
        """Set detector Region of Interest (ROI)"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorROI"
        payload = {
            'detectorName': detector_name
        }
        # Add optional ROI parameters if provided
        if x is not None:
            payload['x'] = x
        if y is not None:
            payload['y'] = y
        if w is not None:
            payload['w'] = w
        if h is not None:
            payload['h'] = h
        response = self.parent.get_json(url, payload=payload)
        return response