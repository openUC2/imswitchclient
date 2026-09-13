import imswitchclient.ImSwitchClient as imc
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time

# ImSwitch API endpoint. None uses $IMSWITCH_API_URL (set for notebooks ImSwitch
# serves itself), else http://localhost:8001/imswitch/api. Behind Caddy/Docker on
# a Raspberry Pi the API sits on port 80: "http://192.168.178.76/imswitch/api".
IMSWITCH_URL = "http://192.168.4.1/imswitch/api"  # docker container on a raspi (port 80)
client = imc.ImSwitchClient(IMSWITCH_URL)

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