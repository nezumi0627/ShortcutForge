from __future__ import annotations
from typing import Any
from .actions import CATALOG
from .ir import IRValidationError


def validate(plan: dict[str, Any]) -> None:
    defined: set[str] = set()
    for i, item in enumerate(plan["actions"]):
        spec = CATALOG.get(item["id"])
        if spec is None:
            raise IRValidationError(f"actions[{i}]: unsupported action {item['id']!r}")
        unknown = set(item.get("params", {})) - set(spec["parameters"])
        if unknown:
            raise IRValidationError(f"actions[{i}]: unsupported parameters: {', '.join(sorted(unknown))}")
        missing = set(spec["parameters"]) - set(item.get("params", {}))
        if missing:
            raise IRValidationError(f"actions[{i}]: missing parameters: {', '.join(sorted(missing))}")
        for value in item.get("params", {}).values():
            if isinstance(value, dict) and set(value) == {"ref"}:
                if not isinstance(value["ref"], str) or value["ref"] not in defined:
                    raise IRValidationError(f"actions[{i}]: undefined output reference {value['ref']!r}")
            elif not isinstance(value, (str, int, float, bool)):
                raise IRValidationError(f"actions[{i}]: parameters must be scalar text/number/boolean values or output references")
        if "as" in item:
            if item["as"] in defined:
                raise IRValidationError(f"actions[{i}]: duplicate output name {item['as']!r}")
            if not spec["output"]:
                raise IRValidationError(f"actions[{i}]: action has no output")
            defined.add(item["as"])
