from __future__ import annotations

import argparse
import getpass
import json
import os
import plistlib
import sys
from collections.abc import Sequence
from pathlib import Path

from .compiler import compile_plan
from .cherri import compile_cherri
from .ir import IRValidationError, load_plan
from .parser import inspect
from .signing import (
    HUBSIGN_API_KEY_ENV,
    sign_with_hubsign,
    sign_with_macos,
    sign_with_shortcuty,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="shortcutforge")
    commands = parser.add_subparsers(dest="command", required=True)

    build = commands.add_parser("build")
    build.add_argument("input", type=Path)
    build.add_argument("-o", "--output", type=Path)

    validate = commands.add_parser("validate")
    validate.add_argument("input", type=Path)

    inspect_command = commands.add_parser("inspect")
    inspect_command.add_argument("input", type=Path)

    sign_command = commands.add_parser("sign")
    sign_command.add_argument("input", type=Path)
    sign_command.add_argument(
        "--via",
        choices=["shortcuty", "hubsign", "macos"],
        default="shortcuty",
        help=(
            "signing tool: Shortcuty (default); Windows supports only Shortcuty, "
            "while HubSign and Apple's macOS signer are available on supported hosts"
        ),
    )

    actions = commands.add_parser("actions")
    actions.add_argument("operation", choices=["list"])
    actions.add_argument("--os", choices=["17", "18", "26", "27"], required=True)
    actions.add_argument("--query", "-q")
    actions.add_argument("--format", choices=["json", "table", "markdown"], default="markdown")
    actions.add_argument("--lang", choices=["en", "ja"], default="en")
    actions.add_argument("--output", "-o", type=Path, help="write Markdown catalog to this file")
    return parser


def _build(args: argparse.Namespace) -> None:
    output = args.output or args.input.with_suffix(".shortcut")
    if args.input.suffix.casefold() == ".cherri":
        compile_cherri(args.input, output)
    else:
        plan = load_plan(args.input)
        compile_plan(plan, output)
    print(output)


def _validate(args: argparse.Namespace) -> None:
    document = plistlib.loads(args.input.read_bytes())
    if not isinstance(document, dict) or not isinstance(document.get("WFWorkflowActions"), list):
        raise ValueError("not a Shortcuts workflow plist")
    print("Valid plist structure (Apple action semantics not verified)")


def _inspect(args: argparse.Namespace) -> None:
    print(json.dumps(inspect(args.input), ensure_ascii=False, indent=2))


def _list_actions(args: argparse.Namespace) -> None:
    from .catalog import get_default_catalog

    catalog = get_default_catalog()
    entries = catalog.list_actions(args.os, query=args.query)

    if args.format == "markdown":
        markdown = catalog.render_markdown(args.os, args.lang, query=args.query)
        if args.output:
            args.output.write_text(markdown, encoding="utf-8")
            print(args.output)
        else:
            print(markdown, end="")
        return

    if args.output:
        raise ValueError("--output can only be used with --format markdown")
    if args.format == "json":
        payload = [entry.to_dict(include_display_name=True) for entry in entries]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    print(f"IDENTIFIER\tNAME/ALIAS\tIOS{args.os}\tPARAMS")
    for entry in entries:
        name = entry.display_name or ", ".join(entry.aliases[:2])
        availability = entry.availability.get(args.os, "unknown")
        print(f"{entry.identifier}\t{name}\t{availability}\t{len(entry.parameters)}")


def _sign(args: argparse.Namespace) -> None:
    output_dir = args.input.parent / "signed"
    if sys.platform == "win32" and args.via != "shortcuty":
        raise ValueError("Windows currently supports only Shortcuty signing; other Windows signing methods are under research")
    if args.via == "shortcuty":
        print(sign_with_shortcuty(args.input, output_dir))
        return
    if args.via == "macos":
        print(sign_with_macos(args.input, output_dir))
        return

    api_key = os.environ.get(HUBSIGN_API_KEY_ENV)
    if not api_key and sys.stdin.isatty():
        api_key = getpass.getpass("HubSign API key (input hidden): ")
    if not api_key:
        raise ValueError(
            f"set {HUBSIGN_API_KEY_ENV} or run sign from an interactive terminal to enter it securely"
        )
    print(sign_with_hubsign(args.input, output_dir, api_key))


_HANDLERS = {
    "build": _build,
    "validate": _validate,
    "inspect": _inspect,
    "actions": _list_actions,
    "sign": _sign,
}


def main(argv: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        _HANDLERS[args.command](args)
    except (IRValidationError, OSError, ValueError, RuntimeError) as exc:
        print(f"shortcutforge: {exc}", file=sys.stderr)
        return 2
    return 0
