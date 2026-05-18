"""JSON formatting helpers used by BLE response code."""

import json


def to_json_string(payload: dict) -> str:
    return json.dumps(payload)


def to_pretty_json(payload: dict) -> str:
    return json.dumps(payload, indent=2)
