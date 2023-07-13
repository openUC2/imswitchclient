==============
ImSwitchClient
==============


.. image:: https://img.shields.io/pypi/v/imswitchclient.svg
        :target: https://pypi.python.org/pypi/imswitchclient

.. image:: https://img.shields.io/travis/beniroquai/imswitchclient.svg
        :target: https://travis-ci.com/beniroquai/imswitchclient

.. image:: https://readthedocs.org/projects/imswitchclient/badge/?version=latest
        :target: https://imswitchclient.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/beniroquai/imswitchclient/shield.svg
     :target: https://pyup.io/repos/github/beniroquai/imswitchclient/
     :alt: Updates



This is a package that connects ImSwitch's REST API to the rest of the world (e.g. jupyter lab)


* Free software: MIT license
* Documentation: https://imswitchclient.readthedocs.io.

Install 
--------
pip install imswitchclient

Features
--------

* remote control ImSwitchUC2 from the Jupyter Notebook with the fastapi endpoints 
* access fastapi on http://localhost:8000/docs


Example
-------

```py
#%%
import imswitchclient.ImSwitchClient as imc

# Instantiate the ImSwitchClient
client = imc.ImSwitchClient()
#%%
# Test the get_positioner_names method
positioner_names = client.get_positioner_names()
print("Positioner Names:", positioner_names)
#%%
#
# Test the move_positioner method
positioner_name = positioner_names[0]
axis = "X"
dist = 1000
is_absolute = True
is_blocking = False

response = client.move_positioner(positioner_name, axis, dist, is_absolute, is_blocking)
print("Move Positioner Response:", response)

#%%
# Test the snap_numpy_to_fastapi method
image_array = client.snap_numpy_to_fastapi()
print("Image Array Shape:", image_array.shape)
```

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
