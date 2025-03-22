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
isHTTPS = True
mPort = 8001
socketPort = 8002

# Instantiate the ImSwitchClient
client = imc.ImSwitchClient(host="localhost", isHttps=isHTTPS, port=mPort, socket_port=socketPort) 
