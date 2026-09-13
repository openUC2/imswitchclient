#!/usr/bin/env python
"""Base-URL resolution of ImSwitchClient.

The same server is reachable as `http://host:8001/imswitch/api` when started
locally and as `http://host/imswitch/api` (port 80) behind Caddy in Docker, so
the constructor has to accept a full URL as well as the historical
host/port/isHttps arguments. Runs standalone: `python tests/test_baseurl.py`.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import imswitchclient.ImSwitchClient as mod  # noqa: E402
from imswitchclient.ImSwitchClient import ImSwitchClient  # noqa: E402

mod.ImSwitchClient.get_json = lambda self, *a, **k: None   # no server needed
mod.socketClient = lambda **kwargs: None

CASES = [
    # a URL without a port means the scheme's port, not the ImSwitch default
    (("http://192.168.178.76/imswitch/api/docs",), {}, "http://192.168.178.76:80/imswitch/api"),
    (("http://192.168.178.76",), {}, "http://192.168.178.76:80/imswitch/api"),
    (("http://100.100.43.118:8001/imswitch/api/docs",), {}, "http://100.100.43.118:8001/imswitch/api"),
    (("https://imswitch.openuc2.com",), {}, "https://imswitch.openuc2.com:443/imswitch/api"),
    # a bare host keeps the historical defaults
    (("192.168.178.76",), {}, "http://192.168.178.76:8001/imswitch/api"),
    ((), {"host": "0.0.0.0", "port": 8001}, "http://0.0.0.0:8001/imswitch/api"),
    ((), {"host": "localhost", "isHttps": True, "port": 8002}, "https://localhost:8002/imswitch/api"),
    ((), {}, "http://localhost:8001/imswitch/api"),
]


def test_base_uri():
    os.environ.pop("IMSWITCH_API_URL", None)
    for args, kwargs, expected in CASES:
        client = ImSwitchClient(*args, **kwargs)
        assert client.base_uri == expected, f"{args}{kwargs} -> {client.base_uri} != {expected}"


def test_env_default_and_override():
    os.environ["IMSWITCH_API_URL"] = "http://127.0.0.1:9000/imswitch/api"
    try:
        assert ImSwitchClient().base_uri == "http://127.0.0.1:9000/imswitch/api"
        # an explicit host still wins over the environment
        assert ImSwitchClient(host="0.0.0.0").base_uri == "http://0.0.0.0:8001/imswitch/api"
    finally:
        os.environ.pop("IMSWITCH_API_URL")


def test_derived_uris():
    client = ImSwitchClient("http://192.168.178.76")
    assert client.base_root_uri == "http://192.168.178.76:80/imswitch"
    assert client.base_swagger_uri == "http://192.168.178.76:80/imswitch/openapi.json"
    assert client.readnoiseManager.dataUrl("recordings/x.tif") == \
        "http://192.168.178.76:80/imswitch/data/recordings/x.tif"


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"ok  {name}")
    print("all good")
