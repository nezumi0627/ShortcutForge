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
    output_ids = {item["as"]: str(uuid.uuid4()).upper() for item in plan["actions"] if "as" in item}
    for item in plan["actions"]:
        spec = CATALOG[item["id"]]
        params = {"UUID": output_ids.get(item.get("as"), str(uuid.uuid4()).upper())}
        if "as" in item:
            params["CustomOutputName"] = item["as"]
        for key, plist_key in spec["parameters"].items():
            value = item.get("params", {}).get(key, spec.get("defaults", {}).get(key))
            if isinstance(value, dict):
                name = value["ref"]
                value = {"Value": {"string": "\ufffc", "attachmentsByRange": {"{0, 1}": {"OutputName": name, "OutputUUID": output_ids[name], "Type": "ActionOutput"}}}, "WFSerializationType": "WFTextTokenString"}
            params[plist_key] = value
        actions.append({"WFWorkflowActionIdentifier": spec["identifier"], "WFWorkflowActionParameters": params})
    document = {"WFWorkflowClientVersion": "1900.0.0.0", "WFWorkflowActions": actions, "WFWorkflowName": plan["name"], "WFWorkflowMinimumClientVersion": 900, "WFWorkflowTypes": []}
    output.write_bytes(plistlib.dumps(document, fmt=plistlib.FMT_BINARY, sort_keys=False))
