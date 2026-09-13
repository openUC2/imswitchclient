#%%
import imswitchclient.ImSwitchClient as imc 
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

stageName=None
scanMax=100
scanMin=-100
scanStep = 50
rescalingFac=10.0
gridScan=True
pixelSize = 1.0
# ImSwitch API endpoint. None uses $IMSWITCH_API_URL (set for notebooks ImSwitch
# serves itself), else http://localhost:8001/imswitch/api. Behind Caddy/Docker on
# a Raspberry Pi the API sits on port 80: "http://192.168.178.76/imswitch/api".
IMSWITCH_URL = "http://localhost:8001/imswitch/api"
socketPort = 8002  # Socket.IO on a different port than the API

client = imc.ImSwitchClient(IMSWITCH_URL, socket_port=socketPort)
