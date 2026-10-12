from __future__ import annotations
import argparse
import json
import plistlib
import sys
from pathlib import Path
from .actions import CATALOG
from .compiler import compile_plan
from .ir import IRValidationError, load_plan
from .parser import inspect
from .signing import sign
from .validator import validate


def main() -> int:
    parser = argparse.ArgumentParser(prog="shortcutforge")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build"); build.add_argument("input", type=Path); build.add_argument("-o", "--output", type=Path)
    val = sub.add_parser("validate"); val.add_argument("input", type=Path)
    ins = sub.add_parser("inspect"); ins.add_argument("input", type=Path)
    sign = sub.add_parser("sign"); sign.add_argument("input", type=Path)
    actions = sub.add_parser("actions"); actions.add_argument("operation", choices=["list"])
    args = parser.parse_args()
    try:
        if args.command == "build":
            plan = load_plan(args.input); out = args.output or args.input.with_suffix(".shortcut"); compile_plan(plan, out); print(out)
        elif args.command == "validate":
            doc = plistlib.loads(args.input.read_bytes())
            if not isinstance(doc, dict) or not isinstance(doc.get("WFWorkflowActions"), list): raise ValueError("not a Shortcuts workflow plist")
            print("Valid plist structure (Apple action semantics not verified)")
        elif args.command == "inspect": print(json.dumps(inspect(args.input), ensure_ascii=False, indent=2))
        elif args.command == "actions": print(json.dumps(CATALOG, ensure_ascii=False, indent=2))
        elif args.command == "sign": print(sign(args.input, args.input.parent / "signed"))
        return 0
    except (IRValidationError, OSError, ValueError, RuntimeError) as exc:
        print(f"shortcutforge: {exc}", file=sys.stderr); return 2
