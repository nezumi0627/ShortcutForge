from __future__ import annotations

import base64
import json
import os
import plistlib
import re
import subprocess
import tempfile
import time
import uuid
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


HUBSIGN_API_URL = "https://routinehub.co/api/v1/sign-shortcut"
HUBSIGN_API_KEY_ENV = "SHORTCUTFORGE_HUBSIGN_API_KEY"


def _gh(args: list[str], *, input_text: str | None = None, timeout: int = 30) -> str:
    result = subprocess.run(["gh", *args], input=input_text, text=True, capture_output=True, timeout=timeout, check=False)
    if result.returncode:
        raise RuntimeError(f"GitHub CLI failed (exit {result.returncode}); check gh auth status and repository permissions")
    return result.stdout


def sign(path: Path, output_dir: Path, timeout: int = 600) -> Path:
    payload = base64.b64encode(path.read_bytes()).decode("ascii")
    if len(payload) > 60_000:
        raise ValueError("shortcut exceeds the 60 KB workflow input limit")
    repo = json.loads(_gh(["repo", "view", "--json", "nameWithOwner"]))["nameWithOwner"]
    nonce = uuid.uuid4().hex
    secret_name = f"SHORTCUTFORGE_{nonce.upper()}"
    _gh(["secret", "set", secret_name], input_text=payload)
    run_id = None
    try:
        body = json.dumps({"ref": "main", "inputs": {"secret_name": secret_name, "filename": f"{nonce}.shortcut", "nonce": nonce}})
        _gh(["api", "--input", "-", "-X", "POST", f"repos/{repo}/actions/workflows/sign.yml/dispatches"], input_text=body)
        started = time.monotonic()
        while time.monotonic() - started < min(timeout, 90):
            rows = json.loads(_gh(["run", "list", "--workflow", "sign.yml", "--limit", "10", "--json", "databaseId,status,displayTitle"]))
            matches = [r for r in rows if r.get("displayTitle") == f"ShortcutForge signing {nonce}"]
            if matches:
                run_id = matches[0]["databaseId"]
                break
            time.sleep(3)
        if run_id is None:
            raise RuntimeError("signing run was not created within 90 seconds")
        while time.monotonic() - started < timeout:
            status = json.loads(_gh(["run", "view", str(run_id), "--json", "status,conclusion"]))
            if status["status"] == "completed":
                if status["conclusion"] != "success":
                    raise RuntimeError(f"signing workflow failed (run {run_id}); inspect its private Actions log")
                output_dir.mkdir(parents=True, exist_ok=True)
                _gh(["run", "download", str(run_id), "--name", f"shortcut-{nonce}", "--dir", str(output_dir)])
                result = output_dir / f"{nonce}.shortcut"
                if not result.is_file():
                    raise RuntimeError("signing artifact did not contain the expected shortcut")
                return result
            time.sleep(5)
        if run_id is not None:
            _gh(["run", "cancel", str(run_id)])
        raise TimeoutError(f"signing workflow exceeded {timeout} seconds (run {run_id})")
    finally:
        _gh(["secret", "remove", secret_name], timeout=30)


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
