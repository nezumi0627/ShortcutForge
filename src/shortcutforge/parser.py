from __future__ import annotations
import plistlib
from pathlib import Path


def inspect(path: Path) -> dict:
    try:
        doc = plistlib.loads(path.read_bytes())
    except (OSError, plistlib.InvalidFileException, ValueError) as exc:
        raise ValueError(f"invalid shortcut plist: {exc}") from exc
    if not isinstance(doc, dict) or not isinstance(doc.get("WFWorkflowActions"), list):
        raise ValueError("not a Shortcuts workflow plist (WFWorkflowActions missing)")
    return {"name": doc.get("WFWorkflowName"), "action_count": len(doc["WFWorkflowActions"]), "actions": [a.get("WFWorkflowActionIdentifier", "<unknown>") for a in doc["WFWorkflowActions"] if isinstance(a, dict)]}
