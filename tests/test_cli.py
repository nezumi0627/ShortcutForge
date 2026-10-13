import json
import plistlib
import tempfile
import unittest
import io
from pathlib import Path
from unittest.mock import patch
from shortcutforge.cli import main
from shortcutforge.compiler import compile_plan
from shortcutforge.ir import IRValidationError, load_plan
from shortcutforge.parser import inspect
from shortcutforge.validator import validate


class ShortcutForgeTests(unittest.TestCase):
    def test_build_cherri_reports_when_external_compiler_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "hello.cherri"
            source.write_text('alert("Hello")\n', encoding="utf-8")
            stderr = io.StringIO()
            with patch.dict("os.environ", {"PATH": ""}), patch("sys.stderr", stderr):
                self.assertEqual(main(["build", str(source)]), 2)
            self.assertIn("Cherri compiler was not found", stderr.getvalue())

    def test_build_cherri_rejects_output_that_would_be_deleted_as_intermediate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "hello.cherri"
            source.write_text('alert("Hello")\n', encoding="utf-8")
            stderr = io.StringIO()
            with patch("shortcutforge.cherri.shutil.which", return_value="cherri.exe"), patch("sys.stderr", stderr):
                self.assertEqual(main(["build", str(source), "-o", str(root / "hello_unsigned.shortcut")]), 2)
            self.assertIn("must not overwrite Cherri's temporary", stderr.getvalue())

    def test_build_cherri_compiles_unsigned_plist_and_moves_it_to_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "hello.cherri"
            output = root / "artifacts" / "hello.shortcut"
            source.write_text('alert("Hello")\n', encoding="utf-8")
            unsigned_output = root / "hello_unsigned.shortcut"

            def compile_source(command, **kwargs):
                self.assertEqual(command[1:], [source.name, "--skip-sign", "--no-ansi"])
                unsigned_output.write_bytes(plistlib.dumps(
                    {"WFWorkflowName": "hello", "WFWorkflowActions": []},
                    fmt=plistlib.FMT_BINARY,
                ))
                return type("Result", (), {"returncode": 0, "stderr": ""})()

            with (
                patch("shortcutforge.cherri.shutil.which", return_value="cherri.exe"),
                patch("shortcutforge.cherri.subprocess.run", side_effect=compile_source),
                patch("sys.stdout", new_callable=io.StringIO) as stdout,
            ):
                self.assertEqual(main(["build", str(source), "-o", str(output)]), 0)

            self.assertEqual(stdout.getvalue().strip(), str(output))
            self.assertEqual(plistlib.loads(output.read_bytes())["WFWorkflowName"], "hello")
            self.assertFalse(unsigned_output.exists())

    def test_compile_binary_plist_and_inspect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, output = root / "plan.json", root / "demo.shortcut"
            source.write_text(json.dumps({"version": 1, "name": "Demo", "actions": [{"id": "text", "params": {"text": "Hello"}}]}))
            compile_plan(load_plan(source), output)
            self.assertTrue(output.read_bytes().startswith(b"bplist00"))
            self.assertEqual(inspect(output)["action_count"], 1)
            self.assertEqual(plistlib.loads(output.read_bytes())["WFWorkflowName"], "Demo")

    def test_reject_unknown_action_and_undefined_reference(self):
        with self.assertRaisesRegex(IRValidationError, "unsupported action"):
            validate({"actions": [{"id": "made_up"}]})
        with self.assertRaisesRegex(IRValidationError, "undefined output reference"):
            validate({"actions": [{"id": "text", "params": {"text": {"ref": "missing"}}}]})

    def test_reject_unknown_top_level_field(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text('{"version":1,"name":"x","actions":[],"unsafe":true}')
            with self.assertRaises(IRValidationError):
                load_plan(p)

    def test_current_date_output_is_encoded_as_shortcut_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "notify.shortcut"
            plan = {"version": 1, "name": "Notify time", "actions": [
                {"id": "current_date", "as": "now"},
                {"id": "notify", "params": {"text": {"ref": "now"}}},
            ]}
            compile_plan(plan, out)
            actions = plistlib.loads(out.read_bytes())["WFWorkflowActions"]
            self.assertEqual(actions[0]["WFWorkflowActionIdentifier"], "is.workflow.actions.date")
            self.assertEqual(actions[0]["WFWorkflowActionParameters"]["WFDateActionMode"], "Current Date")
            uid = actions[0]["WFWorkflowActionParameters"]["UUID"]
            token = actions[1]["WFWorkflowActionParameters"]["WFNotificationActionBody"]
            self.assertEqual(token["Value"]["attachmentsByRange"]["{0, 1}"]["OutputUUID"], uid)
            self.assertTrue(all(action["WFWorkflowActionParameters"].get("UUID") for action in actions))
            self.assertEqual(actions[0]["WFWorkflowActionParameters"]["CustomOutputName"], "now")

    def test_accepts_apple_parameter_keys_and_nested_plist_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "raw.shortcut"
            plan = {"version": 1, "name": "Raw keys", "actions": [
                {"id": "text", "params": {"WFTextActionText": {"Value": {"string": "Hello"}, "WFSerializationType": "WFTextTokenString"}}}
            ]}
            compile_plan(plan, out)
            action = plistlib.loads(out.read_bytes())["WFWorkflowActions"][0]
            self.assertEqual(action["WFWorkflowActionParameters"]["WFTextActionText"]["Value"]["string"], "Hello")

    def test_accepts_explicit_raw_action_identifier_and_parameters(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "raw.shortcut"
            plan = {"version": 1, "name": "Raw action", "actions": [
                {"identifier": "is.workflow.actions.notification", "params": {"WFNotificationActionBody": "Hello"}}
            ]}
            compile_plan(plan, out)
            action = plistlib.loads(out.read_bytes())["WFWorkflowActions"][0]
            self.assertEqual(action["WFWorkflowActionIdentifier"], "is.workflow.actions.notification")
            self.assertEqual(action["WFWorkflowActionParameters"]["WFNotificationActionBody"], "Hello")

    def test_rejects_duplicate_alias_and_internal_parameter(self):
        plan = {"version": 1, "name": "Duplicate", "actions": [
            {"id": "text", "params": {"text": "one", "WFTextActionText": "two"}}
        ]}
        with self.assertRaisesRegex(IRValidationError, "duplicate parameter"):
            validate(plan)

    def test_rejects_non_plist_json_values(self):
        plan = {"version": 1, "name": "Invalid", "actions": [
            {"identifier": "is.workflow.actions.example", "params": {"WFExample": None}}
        ]}
        with self.assertRaisesRegex(IRValidationError, "JSON-compatible plist"):
            validate(plan)


if __name__ == "__main__":
    unittest.main()
