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


def _matches_type(value: Any, value_type: str) -> bool:
    if value_type == "string":
        return isinstance(value, str)
    if value_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if value_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if value_type == "boolean":
        return isinstance(value, bool)
    return True


def _parameter_value(
    params: dict[str, Any], spec: dict[str, Any], alias: str
) -> Any:
    plist_key = spec["parameters"][alias]
    if alias in params:
        return params[alias]
    if plist_key in params:
        return params[plist_key]
    return spec.get("defaults", {}).get(alias)


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
        required_keys = (
            set(spec.get("required", spec["parameters"])) if spec else set()
        )
        present = set(params)
        for alias, plist_key in (spec["parameters"].items() if spec else []):
            if alias in present:
                present.add(plist_key)
            if plist_key in present:
                present.add(alias)
        missing = required_keys - set(spec.get("defaults", {})) - present if spec else set()
        if missing:
            raise IRValidationError(f"actions[{i}]: missing parameters: {', '.join(sorted(missing))}")
        if spec:
            for key in spec.get("references_only", ()):
                if key not in params:
                    continue
                value = params[key]
                if not (isinstance(value, dict) and set(value) == {"ref"}):
                    raise IRValidationError(
                        f"actions[{i}]: parameter {key!r} must reference an earlier action output"
                    )
        for key, value in params.items():
            alias_value = spec is not None and key in spec["parameters"]
            if alias_value and isinstance(value, dict) and set(value) == {"ref"}:
                if not isinstance(value["ref"], str) or value["ref"] not in defined:
                    raise IRValidationError(f"actions[{i}]: undefined output reference {value['ref']!r}")
            elif not _is_json_plist_value(value):
                raise IRValidationError(f"actions[{i}]: parameters must contain JSON-compatible plist values")
            elif alias_value:
                expected_type = spec.get("value_types", {}).get(key)
                if expected_type and not _matches_type(value, expected_type):
                    raise IRValidationError(
                        f"actions[{i}]: parameter {key!r} must be {expected_type}"
                    )
                choices = spec.get("choices", {}).get(key)
                if choices and value not in choices:
                    allowed = ", ".join(repr(choice) for choice in choices)
                    raise IRValidationError(
                        f"actions[{i}]: parameter {key!r} must be one of {allowed}"
                    )
        if spec:
            for key, (condition_key, condition_value) in spec.get(
                "conditional_required", {}
            ).items():
                if (
                    _parameter_value(params, spec, condition_key) == condition_value
                    and key not in params
                    and spec["parameters"][key] not in params
                ):
                    raise IRValidationError(
                        f"actions[{i}]: parameter {key!r} is required when "
                        f"{condition_key!r} is {condition_value!r}"
                    )
            for key, (condition_key, forbidden_values) in spec.get(
                "conditional_forbidden", {}
            ).items():
                if (
                    _parameter_value(params, spec, condition_key)
                    in forbidden_values
                    and (key in params or spec["parameters"][key] in params)
                ):
                    raise IRValidationError(
                        f"actions[{i}]: parameter {key!r} is not available when "
                        f"{condition_key!r} is "
                        f"{_parameter_value(params, spec, condition_key)!r}"
                    )
        if "UUID" in params and (not isinstance(params["UUID"], str) or not params["UUID"].strip()):
            raise IRValidationError(f"actions[{i}]: UUID must be non-empty text")
        if "as" in item:
            if item["as"] in defined:
                raise IRValidationError(f"actions[{i}]: duplicate output name {item['as']!r}")
            if spec and not spec["output"]:
                raise IRValidationError(f"actions[{i}]: action has no output")
            defined.add(item["as"])
