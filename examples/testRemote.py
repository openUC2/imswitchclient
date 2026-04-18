#%%
import imswitchclient.ImSwitchClient as imc
import uuid

# Example: replicating the exact "Experiment" JSON structure from your reference,
# including a point list with a large set of neighbor coordinates.

# Instantiate the ImSwitchClient
client = imc.ImSwitchClient(host="100.112.95.94", port=80, isHttps=False, route="/imswitch/api")

# Turn on LED, set to intensity 100
client.lasersManager.setLaserActive("LED", True)
client.lasersManager.setLaserValue("LED", 100)

# Retrieve hardware parameters (optional, just for demonstration)
mHardwareParameters = client.experimentController.getHardwareParameters()
print("Hardware Parameters:", mHardwareParameters)



def generate_neighbor_point_dict(x_center, y_center, dx, dy, stepsizex, stepsizey):
    neighbors = []
    max_dx = int(round((dx) / stepsizex))
    max_dy = int(round((dy) / stepsizey))

    for dy in range(-max_dy, max_dy + 1):
        for dx in range(-max_dx, max_dx + 1):
            if dx == 0 and dy == 0:
                continue  # skip center point
            neighbor_x = x_center + dx * stepsizex
            neighbor_y = y_center + dy * stepsizey
            neighbors.append({
                "x": neighbor_x,
                "y": neighbor_y,
                "iX": dx,
                "iY": dy
            })

    return {
        "id": str(uuid.uuid4()),
        "name": "",
        "x": x_center,
        "y": y_center,
        "neighborPointList": neighbors
    }

snake_coordinates = generate_neighbor_point_dict(
    x_center=85000,
    y_center=65000,
    dx=3200,  # range for neighbors
    dy=3200,
    stepsizex=800,
    stepsizey=600
)


# Build the experiment JSON exactly like your provided example
experiment_data = {
    "name": "testExperiment",
    "parameterValue": {
        "illumination": mHardwareParameters["illuSources"][0],
        "brightfield": False,
        "darkfield": False,
        "illuIntensities": mHardwareParameters["illuSourceMaxIntensities"][0],
        "differentialPhaseContrast": False,
        "timeLapsePeriod": 1,
        "numberOfImages": 1,
        "autoFocus": False,
        "autoFocusMin": -100,
        "autoFocusMax": 100,
        "autoFocusStepSize": 10,
        "zStack": False,
        "zStackMin": 0,
        "zStackMax": 0,
        "zStackStepSize": 0.1,
        "speed": 10000,  # Motorspeed
        "gains": 20,
        "exposureTimes": 100000,  # from sample hardware parameters
    },
    "pointList": [
        snake_coordinates
    ],
    # The additional fields from the "Experiment" model:
    "number_z_steps": 0,
    "timepoints": 1,
    "experiment_name": "FRAME"
}

# Send the experiment data to startWellplateExperiment
response = client.experimentController.startWellplateExperiment(experiment_data)
print("Experiment started, response:", response)


# wait for 10 seconds and then stop the experiment
import time
time.sleep(20)
# Check the status of the experiment
status = client.experimentController.getExperimentStatus()
print("Experiment status:", status)
client.experimentController.stopExperiment()

# You can optionally pause, resume, or stop as needed:
# pause_resp = client.experimentController.pauseWorkflow()
# resume_resp = client.experimentController.resumeExperiment()
# stop_resp = client.experimentController.stopExperiment()
# force_stop_resp = client.experimentController.forceStopExperiment()
