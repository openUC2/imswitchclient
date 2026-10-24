import time

import requests

# Blocking moves keep the HTTP request open for the whole travel, which can be
# minutes on a long stage. The server itself gives up after ~100 s.
BLOCKING_MOVE_TIMEOUT = 300


class positionersManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        self.allStageNames = self.getAllDeviceNames()
        
    def getAllDeviceNames(self):
        url = f"{self.parent.base_uri}/PositionerController/getPositionerNames"
        headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, headers=headers)
        return response

    def stop(self, positioner_name, axis):
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        
        url = f"{self.parent.base_uri}/PositionerController/stopAxis"
        payload = {
            'positionerName': positioner_name,
            'axis': axis
        }
        response = self.parent.get_json(url, payload=payload)
        return response           

    def movePositionerForever(self, positioner_name=None, axis="X", speed=0, is_stop=False):
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        
        url = f"{self.parent.base_uri}/PositionerController/movePositionerForever"
        payload = {
            'positionerName': positioner_name,
            'axis': axis,
            'speed': speed,
            'is_stop': is_stop
        }
        response = self.parent.get_json(url, payload=payload)
        return response       
            
    def setPositionerSpeed(self, positioner_name, axis, speed):
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        
        url = f"{self.parent.base_uri}/PositionerController/setPositionerSpeed"
        payload = {
            'positionerName': positioner_name,
            'axis': axis,
            'speed': speed
        }
        response = self.parent.get_json(url, payload=payload)
        return response
        
    def movePositioner(self, positioner_name, axis, dist, is_absolute=True, is_blocking=True, speed=10000,
                       timeout=None):
        """Move one axis by/to `dist` µm. `timeout` (s) bounds the HTTP request;
        the default allows long blocking moves (`BLOCKING_MOVE_TIMEOUT`)."""
        if timeout is None:
            timeout = BLOCKING_MOVE_TIMEOUT if is_blocking else 30
        if positioner_name is None:
            positioner_name = self.allStageNames[0]

        url = f"{self.parent.base_uri}/PositionerController/movePositioner"
        payload = {
            'positionerName': positioner_name,
            'axis': axis,
            'dist': dist,
            'isAbsolute': is_absolute,
            'isBlocking': is_blocking, 
            'speed': speed
        }
        #headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, payload=payload, timeout=timeout)
        return response

    def getPositionerPositions(self, id=None):       
        url = f"{self.parent.base_uri}/PositionerController/getPositionerPositions"
        payload = {
        }
        response = self.parent.get_json(url, payload=payload)
        if type(id) == int:
            return response[id]
        return response
    
    def homeAxis(self, positioner_name, axis, is_blocking=False):
        url = f"{self.parent.base_uri}/PositionerController/homeAxis"        
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
            
        payload = {
            'positionerName': positioner_name,
            'axis': axis, 
            'isBlocking': is_blocking
        }
        response = self.parent.get_json(url, payload=payload)
        return response

    def stopAllAxes(self, positioner_name=None):
        """Immediately stop every axis of the positioner"""
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        url = f"{self.parent.base_uri}/PositionerController/stopAllAxes"
        return self.parent.get_json(url, payload={'positionerName': positioner_name})

    def moveRelativeXY(self, dx, dy, positioner_name=None, is_blocking=True, speed=10000):
        """Relative X then Y move in µm; zero components are skipped"""
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        for axis, dist in (("X", dx), ("Y", dy)):
            if dist:
                self.movePositioner(positioner_name, axis, dist, is_absolute=False,
                                    is_blocking=is_blocking, speed=speed)

    def moveAbsoluteXY(self, x, y, positioner_name=None, speed=10000, tolerance_um=10.0,
                       timeout=None, poll=0.5):
        """Absolute X/Y move (µm, user frame) that returns once the stage *reports*
        the target, within `tolerance_um`; returns the final positions.

        `timeout` (s) defaults to twice the travel time at `speed` plus 30 s, so
        a long travel is not cut off. Should an HTTP request time out anyway,
        the move goes on on the server and this keeps polling the position
        instead of failing. Raises TimeoutError if the target is not reached.
        """
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        pos = self.getPositionerPositions()[positioner_name]
        travel = max(abs(x - pos["X"]), abs(y - pos["Y"]))
        if timeout is None:
            timeout = 2 * travel / max(float(speed), 1.0) + 30
        t_end = time.time() + timeout
        for axis, target in (("X", x), ("Y", y)):
            try:
                self.movePositioner(positioner_name, axis, target, is_absolute=True, is_blocking=True,
                                    speed=speed, timeout=max(5.0, t_end - time.time()))
            except requests.exceptions.ReadTimeout:
                pass        # still travelling; the position poll below decides
        while True:
            pos = self.getPositionerPositions()[positioner_name]
            if abs(pos["X"] - x) <= tolerance_um and abs(pos["Y"] - y) <= tolerance_um:
                return pos
            if time.time() > t_end:
                raise TimeoutError(f"stage reports X={pos['X']:.1f} Y={pos['Y']:.1f} µm "
                                   f"{timeout:.0f} s after moving to X={x:.1f} Y={y:.1f} µm")
            time.sleep(poll)
