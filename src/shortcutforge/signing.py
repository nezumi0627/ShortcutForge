from __future__ import annotations

import os
import plistlib
import platform
import re
import subprocess
import tempfile
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HUBSIGN_API_URL = "https://routinehub.co/api/v1/sign-shortcut"
HUBSIGN_API_KEY_ENV = "SHORTCUTFORGE_HUBSIGN_API_KEY"


def sign_with_hubsign(path: Path, output_dir: Path, api_key: str, timeout: int = 60) -> Path:
    """Sign a shortcut through RoutineHub HubSign and save its verified response."""
    if not api_key:
        raise ValueError("HubSign API key is required")
    if not path.is_file():
        raise FileNotFoundError(path)

    shortcut_name = path.stem
    if not shortcut_name or re.search(r"[\r\n\x00]", shortcut_name):
        raise ValueError("shortcut filename contains unsupported control characters")

    unsigned_data = path.read_bytes()
    if unsigned_data.startswith(b"AEA1"):
        raise ValueError("input already has a signed shortcut header")
    try:
        workflow = plistlib.loads(unsigned_data)
    except (plistlib.InvalidFileException, ValueError) as exc:
        raise ValueError("input must be a valid Shortcuts workflow plist") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("WFWorkflowActions"), list):
        raise ValueError("input must be a valid Shortcuts workflow plist")
    boundary = f"----ShortcutForge{uuid.uuid4().hex}"

    parts = [
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"shortcut_name\"\r\n\r\n".encode(),
        shortcut_name.encode("utf-8"),
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"api_key\"\r\n\r\n".encode(),
        api_key.encode("utf-8"),
        f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"shortcut_file\"; filename=\"shortcut.shortcut\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode(),
        unsigned_data,
        f"\r\n--{boundary}--\r\n".encode(),
    ]
    request = Request(
        HUBSIGN_API_URL,
        data=b"".join(parts),
        headers={
            "Accept": "application/octet-stream",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise RuntimeError(f"HubSign returned HTTP {response.status}")
            signed_data = response.read()
    except HTTPError as exc:
        reason = {
            401: "the API key was rejected",
            402: "an active RoutineHub membership with HubSign access is required",
            403: "the account is not authorized to use HubSign",
        }.get(exc.code, "the signing request was rejected")
        raise RuntimeError(f"HubSign error: {reason} (HTTP {exc.code})") from exc
    except URLError as exc:
        raise RuntimeError("Could not reach HubSign; check the network and retry") from exc

    if not signed_data.startswith(b"AEA1"):
        raise RuntimeError("HubSign response does not have the signed shortcut header")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{shortcut_name}.signed.shortcut"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".shortcutforge-", suffix=".tmp", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(signed_data)
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return destination


def sign_with_macos(path: Path, output_dir: Path, timeout: int = 600) -> Path:
    """Sign locally with Apple's macOS Shortcuts command-line tool."""
    if platform.system() != "Darwin":
        raise RuntimeError("the macos signer requires a Mac; choose --via hubsign on Windows or Linux")
    if not path.is_file():
        raise FileNotFoundError(path)

    source_data = path.read_bytes()
    if source_data.startswith(b"AEA1"):
        raise ValueError("input already has a signed shortcut header")
    try:
        workflow = plistlib.loads(source_data)
    except (plistlib.InvalidFileException, ValueError) as exc:
        raise ValueError("input must be a valid Shortcuts workflow plist") from exc
    if not isinstance(workflow, dict) or not isinstance(workflow.get("WFWorkflowActions"), list):
        raise ValueError("input must be a valid Shortcuts workflow plist")
    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{path.stem}.signed.shortcut"
    try:
        with tempfile.TemporaryDirectory(prefix=".shortcutforge-", dir=output_dir) as temp_dir:
            temporary_output = Path(temp_dir) / destination.name
            result = subprocess.run(
                [
                    "shortcuts", "sign", "--mode", "anyone",
                    "--input", str(path), "--output", str(temporary_output),
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            if result.returncode:
                details = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
                raise RuntimeError(f"Apple shortcuts sign failed: {details}")
            if not temporary_output.is_file() or not temporary_output.read_bytes().startswith(b"AEA1"):
                raise RuntimeError("Apple signer did not produce a signed shortcut (AEA1 header missing)")
            os.replace(temporary_output, destination)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Apple shortcuts sign timed out after {timeout} seconds") from exc
    except FileNotFoundError as exc:
        if exc.filename == "shortcuts":
            raise RuntimeError("Apple's shortcuts command was not found; install/update macOS Shortcuts") from exc
        raise
    return destination
