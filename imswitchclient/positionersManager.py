
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
        
        url = f"{self.parent.base_uri}/PositionerController/stop"
        payload = {
            'positionerName': positioner_name,
            'axis': axis
        }
        response = self.parent.get_json(url, payload=payload)
        return response           

    def movePositionerForever(self, speed=(0, 0, 0, 0), is_stop=False):
        if positioner_name is None:
            positioner_name = self.allStageNames[0]
        
        url = f"{self.parent.base_uri}/PositionerController/movePositionerForever"
        payload = {
            'positionerName': positioner_name,
            'speed': speed,
            'isStop': is_stop
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
        
    def movePositioner(self, positioner_name, axis, dist, is_absolute=True, is_blocking=True, speed=10000):
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

        response = self.parent.get_json(url, payload=payload)
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
