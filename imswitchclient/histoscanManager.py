
class histoscanManager(object):
    
    '''
    http://localhost:8001/HistoScanController/startHistoScanTileBasedByParameters?numberTilesX=2&numberTilesY=2&stepSizeX=100&stepSizeY=100&nTimes=1&tPeriod=1&initPosX=0&initPosY=0
    http://localhost:8001/HistoScanController/startStageMapping
    http://localhost:8001/HistoScanController/stopHistoScan
    '''
    
    def __init__(self, parent):
        self.parent = parent
        
    def stopHistoScan(self):
        url = f"{self.parent.base_uri}/HistoScanController/stopHistoScan"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        return response
    
    def startStageScanningPositionlistbased(self, positionList:list, nTimes:int=1, tPeriod:int=1, illuSource:str=None):
        url = f"{self.parent.base_uri}/HistoScanController/startStageScanningPositionlistbased"

        payload = {
            "positionList": str(positionList),
            "nTimes": nTimes,
            "tPeriod": tPeriod,
            "illuSource": illuSource
        }
        if nTimes < 1:
            raise ValueError("nTimes must be greater than 0")
        response = self.parent.get_json(url, payload=payload)
        return response
            

    def startHistoScanTileBasedByParameters(self, numberTilesX, numberTilesY, stepSizeX, stepSizeY, initPosX, initPosY, nTimes=1, tPeriod=1):
        url = f"{self.parent.base_uri}/HistoScanController/startHistoScanTileBasedByParameters"
        payload = {
            "numberTilesX": numberTilesX,
            "numberTilesY": numberTilesY,
            "stepSizeX": stepSizeX,
            "stepSizeY": stepSizeY,
            "nTimes": nTimes,
            "tPeriod": tPeriod,
            "initPosX": initPosX,
            "initPosY": initPosY
        }
        if nTimes < 1:
            raise ValueError("nTimes must be greater than 0")
        response = self.parent.get_json(url, payload=payload)
        return response

    def startStageMapping(self):
        url = f"{self.parent.base_uri}/HistoScanController/startStageMapping"
        payload = {
        }
        response = self.parent.get_json(url, payload=payload)
        return response
    
    def getStatusScanRunning(self):
        url = f"{self.parent.base_uri}/HistoScanController/getStatusScanRunning"
        payload = {
        }
        response = self.parent.get_json(url, payload=payload)
        return response