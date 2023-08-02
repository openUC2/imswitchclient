
class positionersManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def getAllDeviceNames(self):
        url = f"{self.parent.base_uri}/PositionerController/getPositionerNames"
        headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, headers=headers)
        return response
    
    def movePositioner(self, positioner_name, axis, dist, is_absolute=True, is_blocking=True):
        url = f"{self.parent.base_uri}/PositionerController/movePositioner"
        payload = {
            'positionerName': positioner_name,
            'axis': axis,
            'dist': dist,
            'isAbsolute': is_absolute,
            'isBlocking': is_blocking
        }
        #headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, payload=payload)
        return response

    def getPositionerPositions(self):
        url = f"{self.parent.base_uri}/PositionerController/getPositionerPositions"
        payload = {
        }
        response = self.parent.get_json(url, payload=payload)
        return response
