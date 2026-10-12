import json
import plistlib
import tempfile
import unittest
from pathlib import Path
from shortcutforge.compiler import compile_plan
from shortcutforge.ir import IRValidationError, load_plan
from shortcutforge.parser import inspect
from shortcutforge.validator import validate


class ShortcutForgeTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
