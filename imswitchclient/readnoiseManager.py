import time


class readnoiseManager(object):
    """Wraps ReadNoiseCalibrationController: dark/bright stack acquisition.

    Stacks are written server-side under
    ``<dataRoot>/recordings/readnoise_calibration/<sessionId>/<kind>/<kind>_stack.tif``
    and are downloadable through the server's ``/data`` mount (see `dataUrl`).
    """

    def __init__(self, parent):
        self.parent = parent

    def _url(self, func):
        return f"{self.parent.base_uri}/ReadNoiseCalibrationController/{func}"

    def dataUrl(self, relPath):
        """Absolute URL of a file the API reported as a `dataRelPath`/`relPath`"""
        return f"{self.parent.base_root_uri}/data/{relPath.lstrip('/')}"

    # --- status / settings -------------------------------------------------
    def getStatus(self):
        return self.parent.get_json(self._url("getStatus"))

    def getProgress(self):
        return self.parent.get_json(self._url("getProgress"))

    def getDetectorSettings(self, detector_name=None):
        payload = {} if detector_name is None else {'detectorName': detector_name}
        return self.parent.get_json(self._url("getDetectorSettings"), payload=payload)

    def setDetectorSetting(self, name, value, detector_name=None):
        params = {'name': name, 'value': value}
        if detector_name is not None:
            params['detectorName'] = detector_name
        return self.parent.post_json(self._url("setDetectorSetting"), params=params)

    def getHistogram(self, detector_name=None, num_bins=128):
        payload = {'numBins': num_bins}
        if detector_name is not None:
            payload['detectorName'] = detector_name
        return self.parent.get_json(self._url("getHistogram"), payload=payload)

    def setIllumination(self, state="off"):
        """`off` switches all lasers/LEDs off (remembering their state), `restore` puts them back"""
        return self.parent.post_json(self._url("setIllumination"), params={'state': state})

    # --- sessions ----------------------------------------------------------
    def startSession(self, name="", detector_name=None, nBright=20, nDark=20, numBins=100):
        params = {'name': name, 'nBright': nBright, 'nDark': nDark, 'numBins': numBins}
        if detector_name is not None:
            params['detectorName'] = detector_name
        return self.parent.post_json(self._url("startSession"), params=params)

    def listSessions(self):
        return self.parent.get_json(self._url("listSessions"))

    def getSession(self, session_id):
        return self.parent.get_json(self._url("getSession"), payload={'sessionId': session_id})

    def deleteSession(self, session_id):
        return self.parent.post_json(self._url("deleteSession"), params={'sessionId': session_id})

    # --- acquisition -------------------------------------------------------
    def acquireFrames(self, kind="dark", count=None):
        """Start a background capture of `count` frames; poll `getProgress`"""
        params = {'kind': kind}
        if count is not None:
            params['count'] = count
        return self.parent.post_json(self._url("acquireFrames"), params=params)

    def stopAcquisition(self):
        return self.parent.post_json(self._url("stopAcquisition"))

    def acquireStack(self, kind="dark", count=None, poll=2.0, timeout=None, on_progress=None):
        """Blocking `acquireFrames` - returns the final progress dict.

        `timeout` in seconds; None waits forever (a 10 x 1000 s dark stack is a
        ~3 h acquisition, so a timeout is usually not what you want).
        """
        started = self.acquireFrames(kind=kind, count=count)
        if started.get("status") == "error":
            raise RuntimeError(started.get("message", "acquireFrames failed"))
        t0 = time.time()
        while True:
            time.sleep(poll)
            progress = self.getProgress()
            if on_progress:
                on_progress(progress)
            if not progress.get("running"):
                if progress.get("error"):
                    raise RuntimeError(progress["error"])
                return progress
            if timeout is not None and time.time() - t0 > timeout:
                self.stopAcquisition()
                raise TimeoutError(f"{kind} acquisition exceeded {timeout} s")

    def computeCalibration(self, session_id=None, numBins=None,
                           validRangeLow=None, validRangeHigh=None, saturationImage=False):
        params = {'saturationImage': saturationImage}
        for key, value in (('sessionId', session_id), ('numBins', numBins),
                           ('validRangeLow', validRangeLow), ('validRangeHigh', validRangeHigh)):
            if value is not None:
                params[key] = value
        return self.parent.post_json(self._url("computeCalibration"), params=params)
