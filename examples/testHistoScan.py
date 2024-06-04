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


# Instantiate the ImSwitchClient
client = imc.ImSwitchClient(port=8001, isHttps=False)

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
        positionList.append((ix*100,iy*100))
positionList = [(100,200,100), (200,300,400), (500,600,700)]
client.histoscanManager.startStageScanningPositionlistbased(positionList, nTimes=1, tPeriod=1)


# start a stage scan and wait for it to finish 
client.histoscanManager.startHistoScanTileBasedByParameters(numberTilesX, numberTilesY, stepSizeX, stepSizeY, initPosX, initPosY, nTimes, tPeriod)

# wait until scan is finished
while client.histoscanManager.getStatusScanRunning()["ishistoscanRunning"]:
    print("Scan is running")
    time.sleep(1)

# stop any stage scan 
client.histoscanManager.stopHistoScan()
# %%
