import uuid
from typing import List, Dict
import math

class ExperimentController(object):
    """
    REST API interface for ExperimentController, similar to histoscanManager.
    """

    def __init__(self, parent):
        self.parent = parent

    def forceStopExperiment(self):
        url = f"{self.parent.base_uri}/ExperimentController/forceStopExperiment"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def getExperimentStatus(self):
        url = f"{self.parent.base_uri}/ExperimentController/getExperimentStatus"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def getHardwareParameters(self):
        url = f"{self.parent.base_uri}/ExperimentController/getHardwareParameters"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def pauseWorkflow(self):
        url = f"{self.parent.base_uri}/ExperimentController/pauseWorkflow"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def resumeExperiment(self):
        url = f"{self.parent.base_uri}/ExperimentController/resumeExperiment"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def stopExperiment(self):
        url = f"{self.parent.base_uri}/ExperimentController/stopExperiment"
        headers = {"accept": "application/json"}
        return self.parent.get_json(url, headers=headers)

    def startWellplateExperiment(self, experiment_data: dict):
        """
        POST /ExperimentController/startWellplateExperiment
        experiment_data must match the 'Experiment' schema.
        """
        url = f"{self.parent.base_uri}/ExperimentController/startWellplateExperiment"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        return self.parent.post_json(url, payload=experiment_data, headers=headers)

    def createScanCoordinates(
        self,
        center_x: float,
        center_y: float,
        nx: int,
        ny: int,
        x_pixels: int,
        y_pixels: int,
        overlap: float,
        pixel_size: float
    ) -> List[dict]:
        """
        Creates a list of Points (as dicts) around (center_x, center_y),
        using nx, ny grid, calculating dx, dy from x_pixels, y_pixels, overlap, pixel_size.

        Returns a list of dicts for 'pointList' in the final experiment payload.
        Each dict:
           {
             "id": <UUID>,
             "name": "",
             "x": <float>,
             "y": <float>,
             "iX": <int>,
             "iY": <int>,
             "neighborPointList": [ ... ]
           }
        """

        # Calculate the effective step size in X / Y
        # Example: step_x = x_pixels * pixel_size * (1 - overlap)
        step_x = x_pixels * pixel_size * (1.0 - overlap)
        step_y = y_pixels * pixel_size * (1.0 - overlap)

        # We'll place the origin of this grid so that it is centered at (center_x, center_y).
        # A symmetrical approach:
        # For i in [0..nx-1], we do iX = i - (nx-1)/2. Same for y. Then multiply step_x, step_y.
        # This yields a grid centered at center_x, center_y.
        points = []
        for i in range(nx):
            for j in range(ny):
                iX = i - (nx - 1) / 2.0
                iY = j - (ny - 1) / 2.0

                x_coord = center_x + iX * step_x
                y_coord = center_y + iY * step_y

                # Build neighbor offsets for immediate neighbors in the grid:
                neighbor_list = []
                for nx_off in [-1, 0, 1]:
                    for ny_off in [-1, 0, 1]:
                        if nx_off == 0 and ny_off == 0:
                            continue
                        neighbor_i = i + nx_off
                        neighbor_j = j + ny_off
                        if (0 <= neighbor_i < nx) and (0 <= neighbor_j < ny):
                            # Calculate neighbor absolute coords
                            neighbor_x = center_x + (neighbor_i - (nx - 1) / 2.0) * step_x
                            neighbor_y = center_y + (neighbor_j - (ny - 1) / 2.0) * step_y
                            neighbor_list.append({
                                "x": neighbor_x,
                                "y": neighbor_y,
                                "iX": int(neighbor_i - (nx - 1) / 2.0),
                                "iY": int(neighbor_j - (ny - 1) / 2.0)
                            })

                pt = {
                    "id": str(uuid.uuid4()),
                    "name": "",
                    "x": x_coord,
                    "y": y_coord,
                    "iX": int(iX),
                    "iY": int(iY),
                    "neighborPointList": neighbor_list
                }
                points.append(pt)

        return points

    def startWellplateExperimentWithScanCoordinates(
        self,
        center_x: float,
        center_y: float,
        nx: int,
        ny: int,
        x_pixels: int,
        y_pixels: int,
        overlap: float,
        pixel_size: float,
        illumination: str = "LED",
        brightfield: bool = True,
        darkfield: bool = False,
        laser_wave_length: int = 0,
        dpc: bool = False,
        time_lapse_period: float = 0.0,
        number_of_images: int = 1,
        auto_focus: bool = False,
        auto_focus_min: float = 0.0,
        auto_focus_max: float = 0.0,
        auto_focus_step: float = 0.1,
        z_stack: bool = False,
        z_stack_min: float = 0.0,
        z_stack_max: float = 0.0,
        z_stack_step: float = 1.0,
        exposure_time: float = 1000000,  # from sample hardware parameters
        gain: float = 23                # from sample hardware parameters
    ):
        """
        1) Creates scan coordinates around (center_x, center_y) for an Nx x Ny grid.
        2) Builds the appropriate Experiment payload with these coordinates.
        3) Calls startWellplateExperiment with that payload.
        """

        # 1) Get or create the points
        point_list = self.createScanCoordinates(
            center_x=center_x,
            center_y=center_y,
            nx=nx,
            ny=ny,
            x_pixels=x_pixels,
            y_pixels=y_pixels,
            overlap=overlap,
            pixel_size=pixel_size
        )

        # 2) Construct the ParameterValue sub-structure
        param_value = {
            "illumination": illumination,
            "brightfield": brightfield,
            "darkfield": darkfield,
            "laserWaveLength": laser_wave_length,
            "differentialPhaseContrast": dpc,
            "timeLapsePeriod": time_lapse_period,
            "numberOfImages": number_of_images,
            "autoFocus": auto_focus,
            "autoFocusMin": auto_focus_min,
            "autoFocusMax": auto_focus_max,
            "autoFocusStepSize": auto_focus_step,
            "zStack": z_stack,
            "zStackMin": z_stack_min,
            "zStackMax": z_stack_max,
            "zStackStepSize": z_stack_step,
            "exposureTime": exposure_time,
            "gain": gain,
            "resortPointListToSnakeCoordinates": True
        }

        # 3) Build the final experiment JSON
        experiment_data = {
            "name": "WellPlateExperiment_GridScan",
            "parameterValue": param_value,
            "pointList": point_list,
            # Additional fields from the extended "Experiment" model
            "number_z_steps": 0,
            "timepoints": 1,
            "x_pixels": x_pixels,
            "y_pixels": y_pixels,
            "microscope_name": "FRAME",
            "is_multiposition": True,
            "channels": {
                "Ch0": {
                    "is_selected": True,
                    "camera_exposure_time": exposure_time
                }
            },
            "multi_positions": {}
        }

        # 4) Fire off the request
        return self.startWellplateExperiment(experiment_data)

