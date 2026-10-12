from __future__ import annotations

import base64
import json
import subprocess
import time
import uuid
from pathlib import Path


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
