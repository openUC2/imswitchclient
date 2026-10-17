import time


class autofocusManager(object):
    """Server-side autofocus (AutofocusController): a Z step scan around the
    current position with a Gaussian fit of the focus metric. Runs on the
    server; `autoFocusAndWait` polls it to completion."""

    def __init__(self, parent):
        self.parent = parent

    def _url(self, func):
        return f"{self.parent.base_uri}/AutofocusController/{func}"

    def autoFocus(self, rangez=100, resolutionz=10, tSettle=0.1, focusAlgorithm="LAPE",
                  nCropsize=2048, nGauss=0, twoStage=False):
        """Start a scan of ±`rangez` µm in `resolutionz` µm steps; returns at once"""
        payload = {'rangez': rangez, 'resolutionz': resolutionz, 'tSettle': tSettle,
                   'focusAlgorithm': focusAlgorithm, 'nCropsize': nCropsize, 'nGauss': nGauss,
                   'twoStage': twoStage}
        return self.parent.get_json(self._url("autoFocus"), payload=payload)

    def getAutofocusStatus(self):
        """{'state': idle|starting|scanning|fitting|moving_to_focus|finished|aborted|error, ...}"""
        return self.parent.get_json(self._url("getAutofocusStatus"))

    def stopAutofocus(self):
        return self.parent.get_json(self._url("stopAutofocus"))

    def autoFocusAndWait(self, rangez=100, resolutionz=10, poll=0.5, timeout=300, **kwargs):
        """`autoFocus` and wait for it; returns the final status dict.

        Raises if the server refuses to start, the scan ends in error/aborted,
        or `timeout` s pass (the scan is stopped then).
        """
        started = self.autoFocus(rangez=rangez, resolutionz=resolutionz, **kwargs)
        if isinstance(started, dict) and started.get("status") == "error":
            raise RuntimeError(f"autofocus refused: {started.get('message')}")
        t0 = time.time()
        time.sleep(poll)
        while True:
            status = self.getAutofocusStatus()
            state = status.get("state")
            if state in ("finished", "idle") and not status.get("isRunning"):
                return status
            if state in ("error", "aborted"):
                raise RuntimeError(f"autofocus ended with state '{state}'")
            if time.time() - t0 > timeout:
                self.stopAutofocus()
                raise TimeoutError(f"autofocus exceeded {timeout} s")
            time.sleep(poll)
