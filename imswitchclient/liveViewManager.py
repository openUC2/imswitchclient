class liveViewManager(object):
    """Server-side live stream (LiveViewController).

    Long exposures stop the stream on the server; snaps arm the camera on
    demand, so the stream only needs to run for things that converge on
    streamed frames, such as auto exposure.
    """

    def __init__(self, parent):
        self.parent = parent

    def _url(self, func):
        return f"{self.parent.base_uri}/LiveViewController/{func}"

    def startLiveView(self, detector_name=None, protocol="jpeg", params=None, force=False):
        """Start the stream. Refused with status 'long_exposure' above the
        server's long-exposure threshold unless `force` is set."""
        query = {'protocol': protocol, 'force': force}
        if detector_name is not None:
            query['detectorName'] = detector_name
        return self.parent.post_json(self._url("startLiveView"), payload=params, params=query)

    def stopLiveView(self, detector_name=None, stop_camera=True):
        payload = {'stopCamera': stop_camera}
        if detector_name is not None:
            payload['detectorName'] = detector_name
        return self.parent.get_json(self._url("stopLiveView"), payload=payload)

    def getLiveViewActive(self):
        return self.parent.get_json(self._url("getLiveViewActive"))

    def getActiveStreams(self):
        return self.parent.get_json(self._url("getActiveStreams"))

    def getLongExposureInfo(self, detector_name=None):
        """{'exposureMs', 'thresholdMs', 'isLongExposure'}"""
        payload = {} if detector_name is None else {'detectorName': detector_name}
        return self.parent.get_json(self._url("getLongExposureInfo"), payload=payload)
