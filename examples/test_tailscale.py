# !pip install https://github.com/openUC2/imswitchclient/archive/refs/heads/main.zip

# Example: Moving a Stage and Acquiring an Image
import numpy as np
import matplotlib.pyplot as plt
import time
import imswitchclient.ImSwitchClient as imc

# Initialize the client
client = imc.ImSwitchClient(host="openuc2-cloud-bed-11647.queue-macaroni.ts.net", isHttps=True, port=443)

# Retrieve positioner names
positioner_names = client.positionersManager.getAllDeviceNames()
positioner_name = positioner_names[0]

# Get current position
current_positions = client.positionersManager.getPositionerPositions()[positioner_name]
initial_position = (current_positions["X"], current_positions["Y"])

# Turn on illumination
laser_name = client.lasersManager.getLaserNames()[0]
client.lasersManager.setLaserActive(laser_name, True)
client.lasersManager.setLaserValue(laser_name, 512)

# Move the stage and capture an image
def capture_image_at_position(x, y):
    client.positionersManager.movePositioner(positioner_name, "X", x, is_absolute=True, is_blocking=True)
    client.positionersManager.movePositioner(positioner_name, "Y", y, is_absolute=True, is_blocking=True)
    last_frame = client.recordingManager.snapNumpyToFastAPI()
    plt.imshow(last_frame)
    plt.show()




# Example scanning
for ix in range(5):
    for iy in range(5):
        new_x = initial_position[0] + ix * 50
        new_y = initial_position[1] + iy * 50
        capture_image_at_position(new_x, new_y)

# Return stage to initial position
client.positionersManager.movePositioner(positioner_name, "X", initial_position[0], is_absolute=True, is_blocking=True)
client.positionersManager.movePositioner(positioner_name, "Y", initial_position[1], is_absolute=True, is_blocking=True)