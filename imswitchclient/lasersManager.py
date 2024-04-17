
class lasersManager(object):
    
    def __init__(self, parent):
        self.parent = parent
        
    def getLaserNames(self):
        url = f"{self.parent.base_uri}/LaserController/getLaserNames"
        headers = {'accept': 'application/json'}

        response = self.parent.get_json(url, headers=headers)
        return response
    
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
