#!/usr/bin/env python3
"""Regenerate compiler-ready action schemas from a pinned ScPL source snapshot."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "src/shortcutforge/data"
CATALOG_PATH = DATA / "action_catalog.json"
OUTPUT_PATH = DATA / "scpl_ios27_actions.json"
SOURCE_URL = (
    "https://unpkg.com/scpl-macos-updated@2.3.1/built/src/Data/OutActions.json"
)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _action_id(name: str, identifier: str, used: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "action"
    if slug in used:
        slug = f"{slug}_{hashlib.sha256(identifier.encode()).hexdigest()[:8]}"
    if slug in used:
        raise ValueError(f"could not generate unique id for {identifier}")
    used.add(slug)
    return slug


def _builtin_ids() -> set[str]:
    module = ast.parse((ROOT / "src/shortcutforge/actions.py").read_text())
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "CATALOG"
            for target in node.targets
        ) and isinstance(node.value, ast.Dict):
            return {
                key.value
                for key in node.value.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            }
    raise RuntimeError("could not read built-in action IDs from actions.py")


def generate(source_path: Path) -> dict[str, Any]:
    source_actions = _read_json(source_path)
    catalog = _read_json(CATALOG_PATH)["actions"]
    existing = _read_json(OUTPUT_PATH)
    existing_by_identifier = {
        action["identifier"]: action for action in existing["actions"]
    }
    existing_ids = {action["id"] for action in existing["actions"]}
    builtin_ids = _builtin_ids()
    used_ids = existing_ids | builtin_ids
    for action in existing["actions"]:
        action["ios27_parameter_evidence"] = "matched"
        if action["id"] in builtin_ids:
            action["id"] = _action_id(
                action["name"], action["identifier"], used_ids
            )
    result = dict(existing)
    result["filter"] = (
        "action identifier observed in iOS 27.0 Simulator; every parameter key "
        "must also be present in the iOS 27 Simulator parameter-key snapshot; "
        "schemas are raw-key mappings and do not prove runtime behavior"
    )
    result["excluded_due_to_parameter_key_mismatch"] = []

    for identifier, source in sorted(source_actions.items()):
        observed = catalog.get(identifier)
        if not observed or observed.get("availability", {}).get("27") != "observed":
            continue
        params = source.get("Parameters", [])
        source_keys = {param["Key"] for param in params if param.get("Key")}
        observed_keys = {param["key"] for param in observed.get("parameters", [])}
        if not source_keys.issubset(observed_keys):
            name = source.get("Name") or identifier.rsplit(".", 1)[-1]
            result["excluded_due_to_parameter_key_mismatch"].append(
                {
                    "identifier": identifier,
                    "name": name,
                    "reason": (
                        "parameter key is not present in the iOS 27 Simulator "
                        "parameter-key snapshot"
                    ),
                    "source_only_parameter_keys": sorted(source_keys - observed_keys),
                }
            )
            continue
        if identifier in existing_by_identifier:
            continue

        name = source.get("Name") or identifier.rsplit(".", 1)[-1]
        parameters = []
        for param in params:
            key = param.get("Key")
            if not key:
                continue
            normalized = {"key": key, "label": param.get("Label") or key}
            if "DefaultValue" in param:
                normalized["defaultvalue"] = param["DefaultValue"]
            items = param.get("Items")
            if isinstance(items, list):
                normalized["items"] = items
            if param.get("Class"):
                normalized["source_class"] = param["Class"]
            parameters.append(normalized)

        output = source.get("Output")
        result["actions"].append(
            {
                "identifier": identifier,
                "name": name,
                "aliases": [re.sub(r"[^a-z0-9]+", "", name.lower())],
                "category": (source.get("Category") or "other").lower(),
                "parameters": parameters,
                "output": bool(output),
                "source_output": output,
                "id": _action_id(name, identifier, used_ids),
                "ios27_parameter_evidence": "matched",
                "source_app": source.get("AppIdentifier"),
            }
        )

    result["excluded_due_to_parameter_key_mismatch"].sort(
        key=lambda item: item["identifier"]
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Pinned ScPL OutActions.json")
    args = parser.parse_args()
    generated = generate(args.source)
    OUTPUT_PATH.write_text(
        json.dumps(generated, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"Wrote {len(generated['actions'])} schemas to {OUTPUT_PATH}")
    print(
        "Excluded "
        f"{len(generated['excluded_due_to_parameter_key_mismatch'])} key mismatches"
    )


if __name__ == "__main__":
    main()
