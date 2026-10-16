import time


class lasersManager(object):

    def __init__(self, parent):
        self.parent = parent

    def getLaserNames(self):
        url = f"{self.parent.base_uri}/LaserController/getLaserNames"
        headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, headers=headers)
        return response

    def getLaserValueRanges(self, laser_name):
        """(min, max) of the value `setLaserValue` accepts, e.g. (0, 1023) for a PWM channel"""
        url = f"{self.parent.base_uri}/LaserController/getLaserValueRanges"
        return self.parent.get_json(url, payload={'laserName': laser_name})

    def getLaserValue(self, laser_name):
        url = f"{self.parent.base_uri}/LaserController/getLaserValue"
        return self.parent.get_json(url, payload={'laserName': laser_name})

    def getLaserActive(self, laser_name):
        url = f"{self.parent.base_uri}/LaserController/getLaserActive"
        return self.parent.get_json(url, payload={'laserName': laser_name})

    def setLaserValue(self, laser_name, value=0):
        url = f"{self.parent.base_uri}/LaserController/setLaserValue"
        payload = {
            'laserName': laser_name,
            'value': value
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setLaserActive(self, laser_name, active=True):
        url = f"{self.parent.base_uri}/LaserController/setLaserActive"
        payload = {
            "laserName": laser_name,
            "active": active
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def setLaserOn(self, laser_name, value):
        """Set the value and switch the channel on"""
        self.setLaserValue(laser_name, value)
        return self.setLaserActive(laser_name, True)

    def setLaserOff(self, laser_name):
        """Set the value to 0 and switch the channel off"""
        self.setLaserValue(laser_name, 0)
        return self.setLaserActive(laser_name, False)

    def runLaserFor(self, laser_name, value, duration, on_tick=None, tick=1.0, stop_event=None):
        """Drive a channel at `value` for `duration` seconds, then switch it off.

        Meant for actuators wired to a laser/PWM output (pumps, valves). The
        channel is switched off in a `finally`, so an interrupted notebook
        cell (KeyboardInterrupt) or a failed request does not leave a pump
        running. `on_tick(elapsed_s)` is called about every `tick` seconds.
        Setting the `threading.Event` `stop_event` ends the run early.
        """
        self.setLaserOn(laser_name, value)
        try:
            t0 = time.time()
            while (elapsed := time.time() - t0) < duration:
                if stop_event is not None and stop_event.is_set():
                    break
                if on_tick:
                    on_tick(elapsed)
                time.sleep(min(tick, duration - elapsed))
        finally:
            self.setLaserOff(laser_name)
