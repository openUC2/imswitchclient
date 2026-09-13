import imswitchclient.ImSwitchClient as imc
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

# Connect to ImSwitch
hostname = "100.112.95.94"  # Change to the hostname of the computer running ImSwitch
hostname = "192.168.4.1"  # Change to the hostname of the computer running ImSwitch
port = 80 # docker container on raspi
isHttps = False
client = imc.ImSwitchClient(host=hostname, port=port, isHttps=isHttps)

img = client.recordingManager.snapNumpyToFastAPI()



def mySortingFunction(image, threshold=100):
    if np.mean(image)>threshold:
        return True
    else:
        return False
    

if mySortingFunction(img,50):
    print("we move to the right")
    client.positionersManager.movePositioner(None, "X", 100, is_absolute=False, is_blocking=True)
else:
    print("we move to the left")
    client.positionersManager.movePositioner(None, "X", 100, is_absolute=False, is_blocking=True)
    
    
plt.imshow(img)
plt.show()

input()



# compute the diff
for i in range(3):
    img2 = client.recordingManager.snapNumpyToFastAPI()



plt.imshow(np.float32(img)-np.float32(img2))
plt.show()

input()