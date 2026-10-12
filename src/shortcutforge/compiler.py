from __future__ import annotations
import plistlib
import uuid
from pathlib import Path
from typing import Any
from .actions import CATALOG
from .validator import validate


def compile_plan(plan: dict[str, Any], output: Path) -> None:
    validate(plan)
    actions = []
    for item in plan["actions"]:
        spec = CATALOG[item["id"]]
        params = {plist_key: item.get("params", {})[key] for key, plist_key in spec["parameters"].items() if key in item.get("params", {})}
        if spec["output"]:
            params["UUID"] = str(uuid.uuid4()).upper()
        actions.append({"WFWorkflowActionIdentifier": spec["identifier"], "WFWorkflowActionParameters": params})
    document = {"WFWorkflowClientVersion": "1900.0.0.0", "WFWorkflowActions": actions, "WFWorkflowName": plan["name"], "WFWorkflowMinimumClientVersion": 900, "WFWorkflowTypes": []}
    output.write_bytes(plistlib.dumps(document, fmt=plistlib.FMT_BINARY, sort_keys=False))
