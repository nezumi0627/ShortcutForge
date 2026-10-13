from __future__ import annotations

import io
import base64
import hashlib
import json
import plistlib
import tempfile
import unittest
from urllib.error import HTTPError
from pathlib import Path
from unittest.mock import patch

from shortcutforge.cli import main
from shortcutforge.signing import HUBSIGN_API_KEY_ENV
from shortcutforge.signing import sign_with_hubsign, sign_with_macos, sign_with_shortcuty


class HubSignTests(unittest.TestCase):
    @staticmethod
    def write_shortcut(path: Path) -> None:
        path.write_bytes(
            plistlib.dumps(
                {"WFWorkflowName": "Example", "WFWorkflowActions": []},
                fmt=plistlib.FMT_BINARY,
            )
        )

    def test_cli_uses_shortcuty_by_default_without_an_api_key(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.shortcut"
            source.write_bytes(b"bplist00 unsigned")
            result = Path(temp) / "signed" / "input.signed.shortcut"

            with (
                patch.dict("os.environ", {}, clear=True),
                patch("shortcutforge.cli.sign_with_shortcuty", return_value=result) as sign_file,
                patch("sys.stdout", new_callable=io.StringIO),
            ):
                self.assertEqual(main(["sign", str(source)]), 0)

            self.assertEqual(sign_file.call_args.args, (source, source.parent / "signed"))

    def test_cli_selects_hubsign_explicitly_and_requires_its_key(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.shortcut"
            source.write_bytes(b"not read by the signer")
            stderr = io.StringIO()
            with (
                patch.dict("os.environ", {}, clear=True),
                patch("sys.stdin", io.StringIO()),
                patch("sys.stderr", stderr),
                patch("shortcutforge.cli.sign_with_hubsign") as sign_file,
            ):
                self.assertEqual(main(["sign", str(source), "--via", "hubsign"]), 2)
            sign_file.assert_not_called()
            self.assertIn(HUBSIGN_API_KEY_ENV, stderr.getvalue())

    def test_shortcuty_signer_checks_checksums_and_writes_signed_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "BatteryDecisionLab.shortcut"
            self.write_shortcut(source)
            unsigned = source.read_bytes()
            signed = b"AEA1 signed shortcut bytes"
            response_data = {
                "success": True,
                "file": {
                    "format": "AEA1",
                    "input_sha256": hashlib.sha256(unsigned).hexdigest(),
                    "signed_sha256": hashlib.sha256(signed).hexdigest(),
                    "content_base64": base64.b64encode(signed).decode("ascii"),
                },
            }
            response = io.BytesIO(json.dumps(response_data).encode())
            response.status = 200

            with patch("shortcutforge.signing.urlopen", return_value=response) as urlopen:
                result = sign_with_shortcuty(source, root / "signed")

            self.assertEqual(urlopen.call_args.args[0].full_url,
                             "https://sign.shortcuty.app/api/v1/sign?response=json")
            self.assertEqual(result.name, "BatteryDecisionLab.signed.shortcut")
            self.assertEqual(result.read_bytes(), signed)

    def test_shortcuty_signer_rejects_input_checksum_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.shortcut"
            self.write_shortcut(source)
            response = io.BytesIO(json.dumps({"success": True, "file": {
                "format": "AEA1", "input_sha256": "bad", "signed_sha256": "bad",
                "content_base64": base64.b64encode(b"AEA1 bad").decode("ascii"),
            }}).encode())
            response.status = 200
            with patch("shortcutforge.signing.urlopen", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "input checksum"):
                    sign_with_shortcuty(source, root / "signed")
            self.assertFalse((root / "signed" / "input.signed.shortcut").exists())

    def test_cli_selects_native_macos_signer(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.shortcut"
            source.write_bytes(b"not read by the signer")
            result = Path(temp) / "signed" / "input.signed.shortcut"
            with (
                patch("shortcutforge.cli.sign_with_macos", return_value=result) as sign_file,
                patch("sys.stdout", new_callable=io.StringIO),
            ):
                self.assertEqual(main(["sign", str(source), "--via", "macos"]), 0)
            sign_file.assert_called_once_with(source, source.parent / "signed")

    def test_macos_signer_invokes_apple_cli_and_saves_signed_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "Check Battery.shortcut"
            self.write_shortcut(source)

            def run(args, **kwargs):
                self.assertEqual(args[0], "shortcuts")
                self.assertEqual(args[1:4], ["sign", "--mode", "anyone"])
                output = Path(args[args.index("--output") + 1])
                output.write_bytes(b"AEA1 signed by Apple")
                return type("Result", (), {"returncode": 0, "stderr": "", "stdout": ""})()

            with patch("shortcutforge.signing.platform.system", return_value="Darwin"), patch(
                "shortcutforge.signing.subprocess.run", side_effect=run
            ) as run_command:
                output = sign_with_macos(source, root / "signed")

            self.assertEqual(output.name, "Check Battery.signed.shortcut")
            self.assertEqual(output.read_bytes(), b"AEA1 signed by Apple")
            run_command.assert_called_once()

    def test_uploads_unsigned_file_and_saves_signed_response(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "Battery Check.shortcut"
            self.write_shortcut(source)
            response = io.BytesIO(b"AEA1 signed payload")
            response.status = 200

            with patch("shortcutforge.signing.urlopen", return_value=response) as urlopen:
                result = sign_with_hubsign(source, root / "signed", "test-api-key")

            request = urlopen.call_args.args[0]
            body = request.data
            self.assertEqual(request.full_url, "https://routinehub.co/api/v1/sign-shortcut")
            self.assertIn(b'name="shortcut_name"', body)
            self.assertIn(b"Battery Check", body)
            self.assertIn(b'name="api_key"', body)
            self.assertIn(b"test-api-key", body)
            self.assertIn(b"bplist00", body)
            self.assertEqual(result.name, "Battery Check.signed.shortcut")
            self.assertEqual(result.read_bytes(), b"AEA1 signed payload")

    def test_rejects_response_without_signed_shortcut_header(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.shortcut"
            self.write_shortcut(source)
            response = io.BytesIO(b"not a signed shortcut")
            response.status = 200

            with patch("shortcutforge.signing.urlopen", return_value=response):
                with self.assertRaisesRegex(RuntimeError, "signed shortcut header"):
                    sign_with_hubsign(source, root / "signed", "test-api-key")

            self.assertFalse((root / "signed" / "input.signed.shortcut").exists())

    def test_rejects_invalid_plist_before_network_request(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "invalid.shortcut"
            source.write_bytes(b"not a plist")
            with patch("shortcutforge.signing.urlopen") as urlopen:
                with self.assertRaisesRegex(ValueError, "valid Shortcuts workflow"):
                    sign_with_hubsign(source, root / "signed", "test-api-key")
            urlopen.assert_not_called()

    def test_explains_hubsign_membership_error_without_echoing_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.shortcut"
            self.write_shortcut(source)
            error = HTTPError(
                "https://routinehub.co/api/v1/sign-shortcut", 402, "Payment Required", {}, None
            )
            with patch("shortcutforge.signing.urlopen", side_effect=error):
                with self.assertRaisesRegex(RuntimeError, "active .*membership") as raised:
                    sign_with_hubsign(source, root / "signed", "never-print-this-key")
            self.assertNotIn("never-print-this-key", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
