import time


class uc2ConfigManager(object):
    """Board-level calls of UC2ConfigController (CAN-bus power, board status).

    Only the calls a scripted experiment needs; firmware/OTA and motor tuning
    are deliberately not wrapped here.
    """

    def __init__(self, parent):
        self.parent = parent

    def _url(self, func):
        return f"{self.parent.base_uri}/UC2ConfigController/{func}"

    def isBoardConnected(self, strict=False):
        return self.parent.get_json(self._url("uc2_board_is_connected"), payload={'strict': strict})

    def getBusStatus(self):
        """{'power': 1|0|None, 'emergencyActive': bool, 'available': bool, 'estop': {...}}"""
        return self.parent.get_json(self._url("getBusStatus"))

    def setBusPower(self, enable=True):
        """Switch the high-current CAN-bus power that feeds the slave boards.

        Everything on the bus (motor drivers, LED/laser boards, pumps) loses
        power while it is off.
        """
        response = self.parent.get_json(self._url("setBusPower"), payload={'enable': enable})
        if isinstance(response, dict) and response.get("status") == "error":
            raise RuntimeError(f"setBusPower({enable}) failed: {response.get('message')}")
        return response

    def setBusPowerAndWait(self, enable=True, settle=0.0, on_tick=None, tick=1.0, stop_event=None):
        """`setBusPower`, then wait `settle` seconds (e.g. for slaves to boot or
        electronics to quiet down). `on_tick(remaining_s)` is called about
        every `tick` seconds; setting `stop_event` cuts the wait short."""
        response = self.setBusPower(enable)
        t_end = time.time() + settle
        while (remaining := t_end - time.time()) > 0:
            if stop_event is not None and stop_event.is_set():
                break
            if on_tick:
                on_tick(remaining)
            time.sleep(min(tick, remaining))
        return response

    def getBoardTemperature(self):
        return self.parent.get_json(self._url("getBoardTemperature"))
