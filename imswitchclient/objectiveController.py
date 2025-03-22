class objectiveController(object):

    def __init__(self, parent):
        self.parent = parent

    def calibrateObjective(self, homeDirection=None, homePolarity=None):
        url = f"{self.parent.base_uri}/ObjectiveController/calibrateObjective"
        params = {}
        if homeDirection is not None:
            params['homeDirection'] = homeDirection
        if homePolarity is not None:
            params['homePolarity'] = homePolarity
        response = self.parent.get_json(url, payload=params)
        return response

    def getCurrentObjective(self):
        url = f"{self.parent.base_uri}/ObjectiveController/getCurrentObjective"
        response = self.parent.get_json(url)
        return response

    def getStatus(self):
        url = f"{self.parent.base_uri}/ObjectiveController/getstatus"
        response = self.parent.get_json(url)
        return response

    def moveToObjective(self, slot):
        url = f"{self.parent.base_uri}/ObjectiveController/moveToObjective"
        payload = {"slot": slot}
        response = self.parent.get_json(url, payload=payload)
        return response

    def setPositions(self, x1=None, x2=None, z1=None, z2=None, isBlocking=False):
        url = f"{self.parent.base_uri}/ObjectiveController/setPositions"
        payload = {}
        if x1 is not None:
            payload["x1"] = x1
        if x2 is not None:
            payload["x2"] = x2
        if z1 is not None:
            payload["z1"] = z1
        if z2 is not None:
            payload["z2"] = z2
        payload["isBlocking"] = isBlocking
        response = self.parent.get_json(url, payload=payload)
        return response
