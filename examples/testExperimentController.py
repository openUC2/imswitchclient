#%%
import imswitchclient.ImSwitchClient as imc
import uuid

# Example: replicating the exact "Experiment" JSON structure from your reference,
# including a point list with a large set of neighbor coordinates.

# Instantiate the ImSwitchClient
client = imc.ImSwitchClient(host="localhost", port=8001, isHttps=True)

# Turn on LED, set to intensity 100
client.lasersManager.setLaserActive("LED", True)
client.lasersManager.setLaserValue("LED", 100)

# Retrieve hardware parameters (optional, just for demonstration)
mHardwareParameters = client.experimentController.getHardwareParameters()
print("Hardware Parameters:", mHardwareParameters)

# Build the experiment JSON exactly like your provided example
experiment_data = {
    "name": "experiment",
    "parameterValue": {
        "illumination": "Brightfield",
        "brightfield": False,
        "darkfield": False,
        "laserWaveLength": 0,
        "differentialPhaseContrast": False,
        "timeLapsePeriod": 0.1,
        "numberOfImages": 1,
        "autoFocus": False,
        "autoFocusMin": 0,
        "autoFocusMax": 0,
        "autoFocusStepSize": 0.1,
        "zStack": False,
        "zStackMin": 0,
        "zStackMax": 0,
        "zStackStepSize": 0.1,
        "speed": 0  # This field is in your original JSON but not in ParameterValue by default
    },
    "pointList": [
        {
            "id": str(uuid.uuid4()),
            "name": "",
            "x": 42668.321089379206,
            "y": 54159.12253565382,
            "neighborPointList": [
                {"x": 42668.321089379206, "y": 54159.12253565382, "iX": 0, "iY": 0},
                {"x": 42748.321089379206, "y": 54159.12253565382, "iX": 1, "iY": 0},
                {"x": 42588.321089379206, "y": 54159.12253565382, "iX": -1, "iY": 0},
                {"x": 42668.321089379206, "y": 54219.12253565382, "iX": 0, "iY": 1},
                {"x": 42668.321089379206, "y": 54099.12253565382, "iX": 0, "iY": -1},
                {"x": 42828.321089379206, "y": 54159.12253565382, "iX": 2, "iY": 0},
                {"x": 42748.321089379206, "y": 54219.12253565382, "iX": 1, "iY": 1},
                {"x": 42748.321089379206, "y": 54099.12253565382, "iX": 1, "iY": -1},
                {"x": 42508.321089379206, "y": 54159.12253565382, "iX": -2, "iY": 0},
                {"x": 42588.321089379206, "y": 54219.12253565382, "iX": -1, "iY": 1},
                {"x": 42588.321089379206, "y": 54099.12253565382, "iX": -1, "iY": -1},
                {"x": 42668.321089379206, "y": 54279.12253565382, "iX": 0, "iY": 2},
                {"x": 42668.321089379206, "y": 54039.12253565382, "iX": 0, "iY": -2},
                {"x": 42908.321089379206, "y": 54159.12253565382, "iX": 3, "iY": 0},
                {"x": 42828.321089379206, "y": 54219.12253565382, "iX": 2, "iY": 1},
                {"x": 42828.321089379206, "y": 54099.12253565382, "iX": 2, "iY": -1},
                {"x": 42748.321089379206, "y": 54279.12253565382, "iX": 1, "iY": 2},
                {"x": 42748.321089379206, "y": 54039.12253565382, "iX": 1, "iY": -2},
                {"x": 42428.321089379206, "y": 54159.12253565382, "iX": -3, "iY": 0},
                {"x": 42508.321089379206, "y": 54219.12253565382, "iX": -2, "iY": 1},
                {"x": 42508.321089379206, "y": 54099.12253565382, "iX": -2, "iY": -1},
                {"x": 42588.321089379206, "y": 54279.12253565382, "iX": -1, "iY": 2},
                {"x": 42588.321089379206, "y": 54039.12253565382, "iX": -1, "iY": -2},
                {"x": 42668.321089379206, "y": 54339.12253565382, "iX": 0, "iY": 3},
                {"x": 42668.321089379206, "y": 53979.12253565382, "iX": 0, "iY": -3},
                {"x": 42908.321089379206, "y": 54219.12253565382, "iX": 3, "iY": 1},
                {"x": 42908.321089379206, "y": 54099.12253565382, "iX": 3, "iY": -1},
                {"x": 42828.321089379206, "y": 54279.12253565382, "iX": 2, "iY": 2},
                {"x": 42828.321089379206, "y": 54039.12253565382, "iX": 2, "iY": -2},
                {"x": 42748.321089379206, "y": 54339.12253565382, "iX": 1, "iY": 3},
                {"x": 42748.321089379206, "y": 53979.12253565382, "iX": 1, "iY": -3},
                {"x": 42428.321089379206, "y": 54219.12253565382, "iX": -3, "iY": 1},
                {"x": 42428.321089379206, "y": 54099.12253565382, "iX": -3, "iY": -1},
                {"x": 42508.321089379206, "y": 54279.12253565382, "iX": -2, "iY": 2},
                {"x": 42508.321089379206, "y": 54039.12253565382, "iX": -2, "iY": -2},
                {"x": 42588.321089379206, "y": 54339.12253565382, "iX": -1, "iY": 3},
                {"x": 42588.321089379206, "y": 53979.12253565382, "iX": -1, "iY": -3},
                {"x": 42908.321089379206, "y": 54279.12253565382, "iX": 3, "iY": 2},
                {"x": 42908.321089379206, "y": 54039.12253565382, "iX": 3, "iY": -2},
                {"x": 42828.321089379206, "y": 54339.12253565382, "iX": 2, "iY": 3},
                {"x": 42828.321089379206, "y": 53979.12253565382, "iX": 2, "iY": -3},
                {"x": 42428.321089379206, "y": 54279.12253565382, "iX": -3, "iY": 2},
                {"x": 42428.321089379206, "y": 54039.12253565382, "iX": -3, "iY": -2},
                {"x": 42508.321089379206, "y": 54339.12253565382, "iX": -2, "iY": 3},
                {"x": 42508.321089379206, "y": 53979.12253565382, "iX": -2, "iY": -3},
                {"x": 42908.321089379206, "y": 54339.12253565382, "iX": 3, "iY": 3},
                {"x": 42908.321089379206, "y": 53979.12253565382, "iX": 3, "iY": -3},
                {"x": 42428.321089379206, "y": 54339.12253565382, "iX": -3, "iY": 3},
                {"x": 42428.321089379206, "y": 53979.12253565382, "iX": -3, "iY": -3}
            ]
        },
        {
            "id": str(uuid.uuid4()),
            "name": "",
            "x": 44814.80267749491,
            "y": 52791.26662165852,
            "neighborPointList": [
                {"x": 44814.80267749491, "y": 52791.26662165852, "iX": 0, "iY": 0},
                {"x": 44894.80267749491, "y": 52791.26662165852, "iX": 1, "iY": 0},
                {"x": 44734.80267749491, "y": 52791.26662165852, "iX": -1, "iY": 0},
                {"x": 44814.80267749491, "y": 52851.26662165852, "iX": 0, "iY": 1},
                {"x": 44814.80267749491, "y": 52731.26662165852, "iX": 0, "iY": -1},
                {"x": 44974.80267749491, "y": 52791.26662165852, "iX": 2, "iY": 0},
                {"x": 44894.80267749491, "y": 52851.26662165852, "iX": 1, "iY": 1},
                {"x": 44894.80267749491, "y": 52731.26662165852, "iX": 1, "iY": -1},
                {"x": 44654.80267749491, "y": 52791.26662165852, "iX": -2, "iY": 0},
                {"x": 44734.80267749491, "y": 52851.26662165852, "iX": -1, "iY": 1},
                {"x": 44734.80267749491, "y": 52731.26662165852, "iX": -1, "iY": -1},
                {"x": 44974.80267749491, "y": 52851.26662165852, "iX": 2, "iY": 1},
                {"x": 44974.80267749491, "y": 52731.26662165852, "iX": 2, "iY": -1},
                {"x": 44654.80267749491, "y": 52851.26662165852, "iX": -2, "iY": 1},
                {"x": 44654.80267749491, "y": 52731.26662165852, "iX": -2, "iY": -1}
            ]
        }
    ],
    # The additional fields from the "Experiment" model:
    "number_z_steps": 0,
    "timepoints": 1,
    "x_pixels": 0,
    "y_pixels": 0,
    "microscope_name": "FRAME",
    "is_multiposition": False,
    "channels": {
        "Ch0": {
            "is_selected": True,
            "camera_exposure_time": 0.0
        }
    },
    "multi_positions": {}
}

# Send the experiment data to startWellplateExperiment
response = client.experimentController.startWellplateExperiment(experiment_data)
print("Experiment started, response:", response)

# You can optionally pause, resume, or stop as needed:
# pause_resp = client.experimentController.pauseWorkflow()
# resume_resp = client.experimentController.resumeExperiment()
# stop_resp = client.experimentController.stopExperiment()
# force_stop_resp = client.experimentController.forceStopExperiment()
