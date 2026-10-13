"""Optional adapter for the external Cherri Shortcuts compiler."""

from __future__ import annotations

import os
import plistlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


_WORKFLOW_NAME = re.compile(r"^\s*#define\s+name\s+(.+?)\s*$", re.MULTILINE)
_INVALID_FILENAME_CHARS = set('<>:\"/\\|?*')


def _workflow_name(source: Path) -> str:
    try:
        source_text = source.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Cherri source must be UTF-8 text") from exc

    declarations = _WORKFLOW_NAME.findall(source_text)
    name = declarations[-1].strip().strip("\"'") if declarations else source.stem
    if (
        not name
        or name in {".", ".."}
        or any(character in _INVALID_FILENAME_CHARS or ord(character) < 32 for character in name)
    ):
        raise ValueError("Cherri workflow name must be a safe file name")
    return name


def _validate_unsigned_shortcut(data: bytes) -> None:
    if data.startswith(b"AEA1"):
        raise ValueError("Cherri must produce an unsigned shortcut; signing is handled by ShortcutForge")
    try:
        workflow = plistlib.loads(data)
    except (plistlib.InvalidFileException, ValueError) as exc:
        raise ValueError("Cherri output is not a valid Shortcuts plist") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("WFWorkflowActions"), list):
        raise ValueError("Cherri output is not a valid Shortcuts workflow")


def compile_cherri(source: Path, output: Path, timeout: int = 120) -> Path:
    """Compile Cherri source with signing disabled and save a validated plist."""
    source = source.resolve()
    output = output.resolve()
    if source.suffix.casefold() != ".cherri":
        raise ValueError("Cherri input must use the .cherri extension")
    if not source.is_file():
        raise FileNotFoundError(source)
    if source == output:
        raise ValueError("output must not overwrite the Cherri source")

    executable = shutil.which("cherri")
    if executable is None:
        raise RuntimeError(
            "Cherri compiler was not found; install Cherri and ensure it is available on PATH"
        )

    workflow_name = _workflow_name(source)
    intermediate = source.parent / f"{workflow_name}_unsigned.shortcut"
    if output == intermediate.resolve():
        raise ValueError("output must not overwrite Cherri's temporary unsigned file")
    if intermediate.exists():
        raise FileExistsError(
            f"Cherri intermediate already exists: {intermediate}; move or remove it before building"
        )

    try:
        try:
            result = subprocess.run(
                [executable, source.name, "--skip-sign", "--no-ansi"],
                cwd=source.parent,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(f"Cherri compilation exceeded the {timeout}-second timeout") from exc
        except OSError as exc:
            raise RuntimeError("could not start the Cherri compiler") from exc

        if result.returncode != 0:
            raise RuntimeError(
                f"Cherri compilation failed with exit code {result.returncode}; "
                "run Cherri directly for its local diagnostic"
            )
        if not intermediate.is_file():
            raise RuntimeError("Cherri completed without producing the expected unsigned shortcut")

        data = intermediate.read_bytes()
        _validate_unsigned_shortcut(data)
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary_output: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=output.parent,
                prefix=f".{output.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                temporary_output = Path(stream.name)
                stream.write(data)
            os.replace(temporary_output, output)
        finally:
            if temporary_output is not None:
                temporary_output.unlink(missing_ok=True)
    finally:
        intermediate.unlink(missing_ok=True)

    return output
