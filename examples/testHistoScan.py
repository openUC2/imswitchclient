#%%
import imswitchclient.ImSwitchClient as imc 
import time 
# define parameters
numberTilesX = 4
numberTilesY = 4
stepSizeX = 100
stepSizeY = 100
initPosX = 0
initPosY = 0
nTimes = 1
tPeriod = 1


# ImSwitch API endpoint. None uses $IMSWITCH_API_URL (set for notebooks ImSwitch
# serves itself), else http://localhost:8001/imswitch/api. Behind Caddy/Docker on
# a Raspberry Pi the API sits on port 80: "http://192.168.178.76/imswitch/api".
IMSWITCH_URL = "http://localhost:8001/imswitch/api"
client = imc.ImSwitchClient(IMSWITCH_URL)

# turn on laser
client.lasersManager.setLaserActive("LED", True)
client.lasersManager.setLaserValue("LED", 100)

if 0:
    # start a stage mapping
    client.histoscanManager.startStageMapping()


# compute position list 
positionerNames = client.positionersManager.getAllDeviceNames()[0]
currentPositions = client.positionersManager.getPositionerPositions()[positionerNames]
cX, cY = currentPositions["X"], currentPositions["Y"]
positionList = []
for ix in range(3): 
    for iy in range(3):
        positionList.append((ix*100,iy*100,None))
client.histoscanManager.startStageScanningPositionlistbased(positionList, nTimes=1, tPeriod=1)


# wait until scan is finished
while client.histoscanManager.getStatusScanRunning()["ishistoscanRunning"]:
    print("Scan is running")
    time.sleep(1)
    
    
# start a stage scan and wait for it to finish 
client.histoscanManager.startHistoScanTileBasedByParameters(numberTilesX, numberTilesY, stepSizeX, stepSizeY, initPosX, initPosY, nTimes, tPeriod)

# wait until scan is finished
while client.histoscanManager.getStatusScanRunning()["ishistoscanRunning"]:
    print("Scan is running")
    time.sleep(1)

# stop any stage scan 
client.histoscanManager.stopHistoScan()
# %%
