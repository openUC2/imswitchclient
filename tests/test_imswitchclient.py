#!/usr/bin/env python
"""Request-level tests for the managers of `ImSwitchClient`.

No server needed: `get_json` / `post_json` are replaced by a recorder that
stores every call and answers from a canned table, so each test checks which
endpoint a wrapper hits and with which parameters. Runs with pytest or
standalone: `python tests/test_imswitchclient.py`.
"""

import base64
import io
import os
import sys
import threading
import unittest

import numpy as np
import PIL.Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import imswitchclient.ImSwitchClient as mod  # noqa: E402
from imswitchclient.recordingManager import SaveFormat  # noqa: E402

BASE = "http://pi:80/imswitch/api"


class Recorder:
    """Stands in for the HTTP layer. `answers` maps an endpoint suffix
    (e.g. 'RecordingController/getSnapStatus') to a value or a callable."""

    def __init__(self):
        self.calls = []
        self.answers = {}

    def _answer(self, method, path, params, body):
        endpoint = path.replace(BASE + "/", "")
        self.calls.append((method, endpoint, dict(params or {}), body))
        answer = self.answers.get(endpoint)
        return answer(params) if callable(answer) else answer

    def get_json(self, path, payload={}, headers={}, timeout=30):
        return self._answer("GET", path, payload, None)

    def post_json(self, path, payload={}, headers={}, wait_on_task="auto",
                  params=None, timeout=30):
        return self._answer("POST", path, params, payload)

    def endpoints(self):
        return [c[1] for c in self.calls]

    def last(self, endpoint):
        return next(c for c in reversed(self.calls) if c[1] == endpoint)


def make_client():
    rec = Recorder()
    rec.answers["PositionerController/getPositionerNames"] = ["ESP32Stage"]
    mod.ImSwitchClient.get_json = lambda self, *a, **k: rec.get_json(*a, **k)
    mod.ImSwitchClient.post_json = lambda self, *a, **k: rec.post_json(*a, **k)
    mod.socketClient = lambda **kwargs: None
    client = mod.ImSwitchClient("http://pi/imswitch/api")
    rec.calls.clear()
    return client, rec


class TestPositioners(unittest.TestCase):
    def test_stop_uses_stopAxis(self):
        client, rec = make_client()
        client.positionersManager.stop(None, "X")
        self.assertEqual(rec.last("PositionerController/stopAxis")[2],
                         {"positionerName": "ESP32Stage", "axis": "X"})

    def test_move_forever_defaults_to_first_stage(self):
        client, rec = make_client()
        client.positionersManager.movePositionerForever(axis="Y", speed=200, is_stop=False)
        self.assertEqual(rec.last("PositionerController/movePositionerForever")[2],
                         {"positionerName": "ESP32Stage", "axis": "Y", "speed": 200,
                          "is_stop": False})

    def test_stop_all_axes(self):
        client, rec = make_client()
        client.positionersManager.stopAllAxes()
        self.assertIn("PositionerController/stopAllAxes", rec.endpoints())


class TestLasers(unittest.TestCase):
    def test_run_laser_for_switches_off(self):
        client, rec = make_client()
        client.lasersManager.runLaserFor("LASER1", 1023, 0.05, tick=0.01)
        values = [c[2] for c in rec.calls if c[1].startswith("LaserController/set")]
        self.assertEqual(values[0], {"laserName": "LASER1", "value": 1023})
        self.assertEqual(values[-2:], [{"laserName": "LASER1", "value": 0},
                                       {"laserName": "LASER1", "active": False}])

    def test_run_laser_for_switches_off_on_error(self):
        client, rec = make_client()

        def boom(_elapsed):
            raise RuntimeError("tick failed")

        with self.assertRaises(RuntimeError):
            client.lasersManager.runLaserFor("LASER2", 500, 10, on_tick=boom)
        self.assertEqual(rec.last("LaserController/setLaserActive")[2],
                         {"laserName": "LASER2", "active": False})

    def test_run_laser_for_honours_stop_event(self):
        client, rec = make_client()
        stop = threading.Event()
        stop.set()
        client.lasersManager.runLaserFor("LASER1", 1023, 60, stop_event=stop)  # returns at once
        self.assertEqual(rec.last("LaserController/setLaserValue")[2]["value"], 0)


class TestSettings(unittest.TestCase):
    def test_camera_temperature_from_hardware_parameters(self):
        client, rec = make_client()
        rec.answers["SettingsController/getCameraStatus"] = {
            "hardwareParameters": {"temperature_c": -29.6, "tec_target_c": -30.0, "tec_on": True}}
        t = client.settingsManager.getCameraTemperature("Toupcam")
        self.assertEqual((t["temperature"], t["target"], t["tecOn"]), (-29.6, -30.0, True))
        self.assertIsNone(t["fanSpeed"])

    def test_target_temperature_is_a_typed_post(self):
        client, rec = make_client()
        client.settingsManager.setCameraTargetTemperature(-30, detector_name="Toupcam")
        method, _, _, body = rec.last("SettingsController/setDetectorParameterValue")
        self.assertEqual((method, body),
                         ("POST", {"detectorName": "Toupcam", "name": "target_temperature",
                                   "value": -30}))

    def test_detector_mode(self):
        client, rec = make_client()
        client.settingsManager.setDetectorMode("Toupcam", is_auto=False)
        self.assertEqual(rec.last("SettingsController/setDetectorMode")[2],
                         {"detectorName": "Toupcam", "isAuto": False})


class TestRecording(unittest.TestCase):
    def _png_data_url(self):
        buf = io.BytesIO()
        PIL.Image.fromarray(np.arange(12, dtype=np.uint8).reshape(3, 4)).save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    def test_snap_and_wait_polls_until_done(self):
        client, rec = make_client()
        rec.answers["RecordingController/startSnap"] = {"jobId": "j1", "status": "pending"}
        states = iter(["running", "running", "done"])
        rec.answers["RecordingController/getSnapStatus"] = lambda p: {
            "status": next(states), "result": {"relativeFilePath": "/recordings/a.tif"}}
        seen = []
        result = client.recordingManager.snapAndWait("dark", SaveFormat.OME_TIFF, poll=0,
                                                     on_progress=seen.append)
        self.assertEqual(result["relativeFilePath"], "/recordings/a.tif")
        self.assertEqual(len(seen), 3)
        self.assertEqual(rec.last("RecordingController/startSnap")[2]["saveFormat"], 7)
        self.assertEqual(rec.last("RecordingController/getSnapStatus")[2], {"jobId": "j1"})

    def test_snap_and_wait_cancels_on_stop(self):
        client, rec = make_client()
        rec.answers["RecordingController/startSnap"] = {"jobId": "j2"}
        rec.answers["RecordingController/getSnapStatus"] = {"status": "running"}
        stop = threading.Event()
        stop.set()
        with self.assertRaises(InterruptedError):
            client.recordingManager.snapAndWait(poll=0.01, stop_event=stop)
        self.assertEqual(rec.last("RecordingController/cancelSnap")[2], {"jobId": "j2"})

    def test_snap_and_wait_raises_on_server_error(self):
        client, rec = make_client()
        rec.answers["RecordingController/startSnap"] = {"jobId": "j3"}
        rec.answers["RecordingController/getSnapStatus"] = {"status": "error", "error": "no camera"}
        with self.assertRaisesRegex(RuntimeError, "no camera"):
            client.recordingManager.snapAndWait(poll=0)

    def test_preview_to_numpy(self):
        image = mod.recordingManager.previewToNumpy({"previewImage": self._png_data_url()})
        self.assertEqual(image.shape, (3, 4))
        self.assertEqual(int(image[2, 3]), 11)
        self.assertIsNone(mod.recordingManager.previewToNumpy({}))

    def test_data_url(self):
        client, _ = make_client()
        self.assertEqual(client.recordingManager.dataUrl("/recordings/2026/a.tif"),
                         "http://pi:80/imswitch/data/recordings/2026/a.tif")


class TestUC2Config(unittest.TestCase):
    def test_bus_power_error_raises(self):
        client, rec = make_client()
        rec.answers["UC2ConfigController/setBusPower"] = {"status": "error", "message": "no ESP32"}
        with self.assertRaisesRegex(RuntimeError, "no ESP32"):
            client.uc2ConfigManager.setBusPower(False)
        self.assertEqual(rec.last("UC2ConfigController/setBusPower")[2], {"enable": False})

    def test_bus_power_and_wait_stops_early(self):
        client, rec = make_client()
        rec.answers["UC2ConfigController/setBusPower"] = {"status": "success", "power": 1}
        stop = threading.Event()
        stop.set()
        response = client.uc2ConfigManager.setBusPowerAndWait(True, settle=60, stop_event=stop)
        self.assertEqual(response["power"], 1)


class TestLiveView(unittest.TestCase):
    def test_start_live_view_query_and_body(self):
        client, rec = make_client()
        client.liveViewManager.startLiveView("Toupcam", params={"jpeg_quality": 50})
        method, _, query, body = rec.last("LiveViewController/startLiveView")
        self.assertEqual(method, "POST")
        self.assertEqual(query, {"protocol": "jpeg", "force": False, "detectorName": "Toupcam"})
        self.assertEqual(body, {"jpeg_quality": 50})


if __name__ == "__main__":
    unittest.main()
