import json
from pathlib import Path
import pickle
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


def save_pickle_state(directory, state):
    path = Path(directory) / ".plan_state.pickle"
    backup = path.with_suffix(".plan_state.pickle.bak")
    if path.exists():
        path.rename(backup)
    with open(path, "wb") as f:
        pickle.dump(state, f)


def load_pickle_state(directory="."):
    path = Path(directory) / ".plan_state.pickle"
    if path.exists():
        with open(path, "rb") as f:
            return pickle.load(f)
    return []


def save_render_json(directory, plan_resources):
    path = Path(directory) / ".plan_render.json"

    def resource_to_dict(r):
        return {"kind": r.kind, "id": r.id, "spec": r.spec}
    data = [resource_to_dict(r) for r in plan_resources]
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
