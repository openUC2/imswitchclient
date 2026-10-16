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

    def getDetectorParameter(self, parameter_name, detector_name=None):
        """Read one parameter live from the camera (e.g. 'temperature', 'exposure', 'gain')"""
        url = f"{self.parent.base_uri}/SettingsController/getDetectorParameter"
        payload = {'parameterName': parameter_name}
        if detector_name is not None:
            payload['detectorName'] = detector_name
        return self.parent.get_json(url, payload=payload)

    def setDetectorBlackLevel(self, detector_name, black_level):
        url = f"{self.parent.base_uri}/SettingsController/setDetectorBlackLevel"
        payload = {'detectorName': detector_name, 'blackLevel': black_level}
        return self.parent.get_json(url, payload=payload)

    def setDetectorMode(self, detector_name=None, is_auto=True):
        """Switch the camera's auto exposure on (`is_auto=True`) or back to manual"""
        url = f"{self.parent.base_uri}/SettingsController/setDetectorMode"
        payload = {'isAuto': is_auto}
        if detector_name is not None:
            payload['detectorName'] = detector_name
        return self.parent.get_json(url, payload=payload)

    def setDetectorExposureOnce(self, detector_name=None, reset_delay_ms=1500):
        """One auto-exposure pass, then back to manual after `reset_delay_ms`.

        Auto exposure converges on streamed frames, so the live view has to
        run (and the exposure be short) while it does.
        """
        url = f"{self.parent.base_uri}/SettingsController/setDetectorExposureOnce"
        payload = {'resetDelayMs': reset_delay_ms}
        if detector_name is not None:
            payload['detectorName'] = detector_name
        return self.parent.get_json(url, payload=payload)

    def getCameraTemperature(self, detector_name=None):
        """Sensor temperature and cooler state of a TEC camera, in °C.

        Returns {'temperature', 'target', 'tecOn', 'fanSpeed', 'overTemperature'};
        a field is None when the camera does not report it.
        """
        status = self.getCameraStatus(detector_name)
        hw = status.get('hardwareParameters') or {}
        return {
            'temperature': hw.get('temperature_c'),
            'target': hw.get('tec_target_c'),
            'tecOn': hw.get('tec_on'),
            'fanSpeed': hw.get('fan_speed'),
            'overTemperature': hw.get('tec_over_temperature'),
        }

    def setCameraTargetTemperature(self, temperature_c, detector_name=None):
        """Cooler set point in °C. The camera clamps it to its supported range."""
        return self.setDetectorParameterValue('target_temperature', temperature_c,
                                              detector_name=detector_name)
