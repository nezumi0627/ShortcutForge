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
    action_uuids = {}
    for item in plan["actions"]:
        raw_uuid = item.get("params", {}).get("UUID")
        action_uuids[id(item)] = raw_uuid or str(uuid.uuid4()).upper()
    output_ids = {item["as"]: action_uuids[id(item)] for item in plan["actions"] if "as" in item}
    for item in plan["actions"]:
        spec = CATALOG.get(item["id"]) if "id" in item else None
        params = dict(item.get("params", {}))
        if spec:
            for key, plist_key in spec["parameters"].items():
                if key not in params and plist_key not in params and key in spec.get("defaults", {}):
                    params[plist_key] = spec["defaults"][key]
                if key not in params:
                    continue
                value = params.pop(key)
                if isinstance(value, dict) and set(value) == {"ref"}:
                    name = value["ref"]
                    value = {"Value": {"string": "\ufffc", "attachmentsByRange": {"{0, 1}": {"OutputName": name, "OutputUUID": output_ids[name], "Type": "ActionOutput"}}}, "WFSerializationType": "WFTextTokenString"}
                params[plist_key] = value
        params.setdefault("UUID", action_uuids[id(item)])
        if "as" in item:
            params.setdefault("CustomOutputName", item["as"])
        identifier = spec["identifier"] if spec else item["identifier"]
        actions.append({"WFWorkflowActionIdentifier": identifier, "WFWorkflowActionParameters": params})
    document = {"WFWorkflowClientVersion": "1900.0.0.0", "WFWorkflowActions": actions, "WFWorkflowName": plan["name"], "WFWorkflowMinimumClientVersion": 900, "WFWorkflowTypes": []}
    output.write_bytes(plistlib.dumps(document, fmt=plistlib.FMT_BINARY, sort_keys=False))
