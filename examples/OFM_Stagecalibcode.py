# %%
# This is a notebook to test the stage calibration. It is based on the example script testStageCalibration.py. The notebook is used to test the stage calibration and to visualize the results.
#%%
import imswitchclient.ImSwitchClient as imc 
import numpy as np
import matplotlib.pyplot as plt
import json
from skimage.registration import phase_cross_correlation

from OFMStageScanClass import OFMStageScanClass

stageName=None
scanMax=100
scanMin=-100
scanStep = 50
rescalingFac=10.0
gridScan=True
pixelSize = 1.0
isHTTPS = False
mPort = 8001

# Instantiate the ImSwitchClient
client = imc.ImSwitchClient(host="localhost", isHttps=isHTTPS, port=mPort) 


# %% set laser value 
laser_names = client.lasersManager.getLaserNames()
print(laser_names)
mLaserName = laser_names[0]
client.lasersManager.setLaserActive(mLaserName, True)
client.lasersManager.setLaserValue(mLaserName, 1023)
#%%
# Test the get_positioner_names method
positioner_names = client.positionersManager.getAllDeviceNames()
positioner_name = positioner_names[0]
currentPositions = client.positionersManager.getPositionerPositions()[positioner_name]
initialPosition = (currentPositions["X"], currentPositions["Y"])
initialPosiionZ = currentPositions["Z"]
#client.positionersManager.movePositioner(positioner_name, dist=0, axis="X")

# initiate and start the stage calibration in X/Y
pixelSize = 0.3 # µm
mumPerStep = 0.3 # µm
calibFilePath = "calibFile.json"
csm_extension = OFMStageScanClass(client, calibration_file_path=calibFilePath, effPixelsize=pixelSize, stageStepSize=mumPerStep)
mData = csm_extension.calibrate_xy(return_backlash_data=1)

if 1:
    result = mData
    print(f"Calibration result:")
    for k, v in result.items():
        print(f"    {k}:")
        for l, w in v.items():
            if len(str(w)) < 50:
                print(f"        {l}: {w}")
            else:
                print(f"        {l}: too long to print")
else:
    # print the result 
    with open(calibFilePath, "r") as fd:
        result = json.load(fd)
        print(f"Calibration result:")
        for k, v in result.items():
            print(f"    {k}:")
            for l, w in v.items():
                if len(str(w)) < 50:
                    print(f"        {l}: {w}")
                else:
                    print(f"        {l}: too long to print")



