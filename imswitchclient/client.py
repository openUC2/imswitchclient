"""Backwards-compatible alias.

The client used to exist twice, and this copy pointed at `/imswitch/api/v2`,
a route the server does not serve. Everything lives in `ImSwitchClient.py` now.
"""
from .ImSwitchClient import ImSwitchClient, parseBaseUrl  # noqa: F401
