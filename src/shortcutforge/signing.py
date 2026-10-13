from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
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
SHORTCUTY_API_URL = "https://sign.shortcuty.app/api/v1/sign?response=json"


def sign_with_shortcuty(path: Path, output_dir: Path, timeout: int = 120) -> Path:
    """Sign via Shortcuty's keyless service and verify its response checksums."""
    if not path.is_file():
        raise FileNotFoundError(path)

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
    body = b"".join(
        (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"shortcut.shortcut\"\r\nContent-Type: application/octet-stream\r\n\r\n".encode(),
            unsigned_data,
            f"\r\n--{boundary}--\r\n".encode(),
        )
    )
    request = Request(
        SHORTCUTY_API_URL,
        data=body,
        headers={
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            response_data = response.read(10_000_001)
    except HTTPError as exc:
        exc.close()
        raise RuntimeError(f"Shortcuty signing service rejected the request (HTTP {exc.code})") from exc
    except URLError as exc:
        raise RuntimeError("Could not reach Shortcuty signing service; check the network and retry") from exc

    if len(response_data) > 10_000_000:
        raise RuntimeError("Shortcuty response exceeded the 10 MB safety limit")
    try:
        payload = json.loads(response_data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Shortcuty returned an invalid JSON response") from exc
    file_info = payload.get("file") if isinstance(payload, dict) else None
    if not isinstance(file_info, dict) or payload.get("success") is not True:
        raise RuntimeError("Shortcuty did not confirm that it signed the shortcut")
    if file_info.get("format") != "AEA1":
        raise RuntimeError("Shortcuty response is not in the AEA1 signed shortcut format")
    input_checksum = file_info.get("input_sha256")
    if not isinstance(input_checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", input_checksum):
        raise RuntimeError("Shortcuty response has an invalid input checksum")
    if not hmac.compare_digest(input_checksum, hashlib.sha256(unsigned_data).hexdigest()):
        raise RuntimeError("Shortcuty response input checksum does not match the uploaded shortcut")

    encoded = file_info.get("content_base64")
    if not isinstance(encoded, str):
        raise RuntimeError("Shortcuty response does not contain the signed file")
    try:
        signed_data = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError("Shortcuty returned invalid base64 file data") from exc
    if not signed_data.startswith(b"AEA1"):
        raise RuntimeError("Shortcuty response is missing the signed shortcut header")
    signed_sha = hashlib.sha256(signed_data).hexdigest()
    signed_checksum = file_info.get("signed_sha256")
    if not isinstance(signed_checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", signed_checksum):
        raise RuntimeError("Shortcuty response has an invalid signed checksum")
    if not hmac.compare_digest(signed_checksum, signed_sha):
        raise RuntimeError("Shortcuty response signed checksum does not match the returned file")

    output_dir.mkdir(parents=True, exist_ok=True)
    destination = output_dir / f"{path.stem}.signed.shortcut"
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=output_dir, prefix=".shortcutforge-", suffix=".tmp", delete=False) as stream:
            temp_path = Path(stream.name)
            stream.write(signed_data)
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return destination


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
        exc.close()
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
