from __future__ import annotations
from typing import Any
from .actions import CATALOG
from .ir import IRValidationError


def _is_json_plist_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (str, bool, int)):
        return True
    if isinstance(value, float):
        return value == value and abs(value) != float("inf")
    if isinstance(value, list):
        return all(_is_json_plist_value(item) for item in value)
    if isinstance(value, dict):
        return all(isinstance(key, str) and _is_json_plist_value(item) for key, item in value.items())
    return False


def validate(plan: dict[str, Any]) -> None:
    defined: set[str] = set()
    for i, item in enumerate(plan["actions"]):
        spec = CATALOG.get(item["id"]) if "id" in item else None
        if "id" in item and spec is None:
            raise IRValidationError(f"actions[{i}]: unsupported action {item['id']!r}; use identifier for a raw Apple action")
        if "identifier" in item and not item["identifier"].strip():
            raise IRValidationError(f"actions[{i}]: identifier cannot be empty")
        params = item.get("params", {})
        if spec:
            accepted = set(spec["parameters"]) | set(spec["parameters"].values())
            unknown = set(params) - accepted
            if unknown:
                raise IRValidationError(f"actions[{i}]: unsupported parameters: {', '.join(sorted(unknown))}")
            for alias, plist_key in spec["parameters"].items():
                if alias != plist_key and alias in params and plist_key in params:
                    raise IRValidationError(f"actions[{i}]: duplicate parameter supplied as {alias!r} and {plist_key!r}")
        required_keys = set(spec["parameters"]) if spec else set()
        present = set(params)
        for alias, plist_key in (spec["parameters"].items() if spec else []):
            if alias in present:
                present.add(plist_key)
            if plist_key in present:
                present.add(alias)
        missing = required_keys - set(spec.get("defaults", {})) - present if spec else set()
        if missing:
            raise IRValidationError(f"actions[{i}]: missing parameters: {', '.join(sorted(missing))}")
        for key, value in params.items():
            alias_value = spec is not None and key in spec["parameters"]
            if alias_value and isinstance(value, dict) and set(value) == {"ref"}:
                if not isinstance(value["ref"], str) or value["ref"] not in defined:
                    raise IRValidationError(f"actions[{i}]: undefined output reference {value['ref']!r}")
            elif not _is_json_plist_value(value):
                raise IRValidationError(f"actions[{i}]: parameters must contain JSON-compatible plist values")
        if "UUID" in params and (not isinstance(params["UUID"], str) or not params["UUID"].strip()):
            raise IRValidationError(f"actions[{i}]: UUID must be non-empty text")
        if "as" in item:
            if item["as"] in defined:
                raise IRValidationError(f"actions[{i}]: duplicate output name {item['as']!r}")
            if spec and not spec["output"]:
                raise IRValidationError(f"actions[{i}]: action has no output")
            defined.add(item["as"])
