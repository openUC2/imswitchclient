from PIL import Image
import numpy as np
import io
import json

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
            

    def startStageScanningPositionlistbased(self, positionList:str, nTimes:int=1, tPeriod:int=1, illuSource:str=None):
        '''
        https://localhost:8001/HistoScanController/startStageScanningPositionlistbased?positionList=dadf&nTimes=1&tPeriod=0
        
        positionList: list of tuples with X/Y positions (e.g. "[(10, 10, 100), (100, 100, 100)]")
        nTimes: number of times to repeat the scan
        tPeriod: time between scans
        '''
        
        url = f"{self.parent.base_uri}/HistoScanController/startStageScanningPositionlistbased"
        payload = {
            "positionList": positionList,
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
    
    def getLastStitchedImage(self):
        '''
        https://localhost:8001/HistoScanController/
        Retrieve numpy image based on 
        return Response(im_bytes, headers=headers, media_type='image/png')
        '''
        url = f"{self.parent.base_uri}/HistoScanController/getLastStitchedImage"
        headers = {'accept': 'application/json'}
        response = self.parent.get_json(url, headers=headers)
        content_type = response.headers.get('content-type')
        if content_type == 'image/png':
            image_data = response.content
            image = Image.open(io.BytesIO(image_data))
            return np.array(image)
        else:
            raise ValueError("Unexpected response content-type. Expected 'image/png'.")
        
        
    def startStageScanning(self, minPosX:float=None, maxPosX:float=None, minPosY:float=None, maxPosY:float=None, 
                           overlap:float=None, nTimes:int=1, tPeriod:int=0, positionList:list=None, 
                           isStitchAshlar:bool=False, isStitchAshlarFlipX:bool=False, isStitchAshlarFlipY:bool=False, 
                           resizeFactor=0.25):
        '''
        generic stage scan, rather low-level
        '''
        url = f"{self.parent.base_uri}/HistoScanController/startStageScanning"
        payload = {
            "minPosX": minPosX,
            "maxPosX": maxPosX,
            "minPosY": minPosY,
            "maxPosY": maxPosY,
            "overlap": overlap,
            "nTimes": nTimes,
            "tPeriod": tPeriod,
            "positionList": json.dumps(positionList),
            "isStitchAshlar": isStitchAshlar,
            "isStitchAshlarFlipX": isStitchAshlarFlipX,
            "isStitchAshlarFlipY": isStitchAshlarFlipY,
            "resizeFactor": resizeFactor
        }
        response = self.parent.get_json(url, payload=payload)
        return response