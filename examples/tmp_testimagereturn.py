import imswitchclient.ImSwitchClient as imc 
import numpy as np
# Instantiate the ImSwitchClient
client = imc.ImSwitchClient()   
np.max( client.recordingManager.snapNumpyToFastAPI(resizeFactor=.1))