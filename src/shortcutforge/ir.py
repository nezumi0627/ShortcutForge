"""Versioned, strictly typed JSON intermediate representation."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class IRValidationError(ValueError):
    pass


def load_plan(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IRValidationError(f"cannot read JSON plan: {exc}") from exc
    if not isinstance(data, dict) or set(data) - {"version", "name", "actions"}:
        raise IRValidationError("plan must be an object with only version, name, actions")
    if data.get("version") != 1 or not isinstance(data.get("name"), str) or not data["name"].strip():
        raise IRValidationError("version must be 1 and name must be non-empty text")
    if not isinstance(data.get("actions"), list):
        raise IRValidationError("actions must be a list")
    for i, action in enumerate(data["actions"]):
        if not isinstance(action, dict) or set(action) - {"id", "params", "as"}:
            raise IRValidationError(f"actions[{i}] must contain only id, params, and optional as")
        if not isinstance(action.get("id"), str) or not isinstance(action.get("params", {}), dict):
            raise IRValidationError(f"actions[{i}] requires a string id and object params")
        if "as" in action and not isinstance(action["as"], str):
            raise IRValidationError(f"actions[{i}].as must be a string")
    return data
