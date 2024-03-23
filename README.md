
# ImSwitchClient

[![PyPI Version](https://img.shields.io/pypi/v/imswitchclient.svg)](https://pypi.python.org/pypi/imswitchclient)
[![Build Status](https://img.shields.io/travis/beniroquai/imswitchclient.svg)](https://travis-ci.com/beniroquai/imswitchclient)
[![Documentation Status](https://readthedocs.org/projects/imswitchclient/badge/?version=latest)](https://imswitchclient.readthedocs.io/en/latest/?version=latest)
[![Updates](https://pyup.io/repos/github/beniroquai/imswitchclient/shield.svg)](https://pyup.io/repos/github/beniroquai/imswitchclient/)

This is a package that connects ImSwitch's REST API to the rest of the world (e.g. jupyter lab)

- Free software: MIT license
- Documentation: [https://imswitchclient.readthedocs.io](https://imswitchclient.readthedocs.io).

## Install

```bash
pip install imswitchclient
```

## Features

- remote control ImSwitchUC2 from the Jupyter Notebook with the fastapi endpoints
- access fastapi on http://localhost:8000/docs

## Example

```python
#%%
#%%
import imswitchclient.ImSwitchClient as imc 
import numpy as np
import matplotlib.pyplot as plt
import cv2


stageName=None
scanMax=100
scanMin=-100
scanStep = 50
rescalingFac=10.0
gridScan=True


# Instantiate the ImSwitchClient
client = imc.ImSwitchClient()
#%%
# Test the get_positioner_names method
positioner_names = client.positionersManager.getAllDeviceNames()
print("Positioner Names:", positioner_names)
#%%
#
# Test the move_positioner method
positioner_name = positioner_names[0]
axis = "X"
dist = 1000
is_absolute = True
is_blocking = False

response = client.positionersManager.movePositioner(positioner_name, axis, dist, is_absolute, is_blocking)
print("Move Positioner Response:", response)

#%%
# Test the snap_numpy_to_fastapi method
image_array = client.recordingManager.snapNumpyToFastAPI()
print("Image Array Shape:", image_array.shape)
```

## Credits

This package was created with Cookiecutter and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template.
