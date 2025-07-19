import json
from pathlib import Path
import re


def parse_timeout(timeout_str):
    if not timeout_str:
        return 0
    match = re.match(r"^(\d+)(ms|s|m|h)?$", timeout_str)
    if not match:
        raise ValueError(f"Invalid timeout format: {timeout_str}")
    value, unit = match.groups()
    value = int(value)
    if unit == "ms":
        return value / 1000
    elif unit == "s" or unit is None:
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    else:
        raise ValueError(f"Unknown unit in timeout: {unit}")


def load_state_file(directory="."):
    path = Path(directory) / ".plan_state.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"resources": []}


def save_state_file(directory, state):
    path = Path(directory) / ".plan_state.json"
    backup = path.with_suffix(".plan_state.json.bak")
    if path.exists():
        path.rename(backup)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)


