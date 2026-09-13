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
    def getDetectorParameters(self):
        """Short summary (exposure/gain/blacklevel/mode/limits) of the current detector"""
        url = f"{self.parent.base_uri}/SettingsController/getDetectorParameters"
        return self.parent.get_json(url)

    def getDetectorParameterTree(self, detector_name=None):
        """Full camera state as JSON: hardware info + every parameter with type/limits"""
        url = f"{self.parent.base_uri}/SettingsController/getDetectorParameterTree"
        payload = {} if detector_name is None else {'detectorName': detector_name}
        return self.parent.get_json(url, payload=payload)

    def setDetectorParameterValue(self, name, value, detector_name=None):
        """Set one parameter (any JSON type, cast server-side) and get the refreshed tree back"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorParameterValue"
        payload = {'detectorName': detector_name, 'name': name, 'value': value}
        return self.parent.post_json(url, payload=payload)

    def getCameraStatus(self, detector_name=None):
        """Camera status incl. temperature, firmware and current parameter values"""
        url = f"{self.parent.base_uri}/SettingsController/getCameraStatus"
        payload = {} if detector_name is None else {'detectorName': detector_name}
        return self.parent.get_json(url, payload=payload)
