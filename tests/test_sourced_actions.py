from __future__ import annotations

import json
import plistlib
import tempfile
import unittest
from importlib.resources import files
from pathlib import Path

from shortcutforge.actions import CATALOG, SOURCED_CATALOG
from shortcutforge.compiler import compile_plan


class SourcedActionTests(unittest.TestCase):
    def test_generated_catalog_has_unique_ids_and_ios27_only_evidence(self):
        data = json.loads(
            files("shortcutforge")
            .joinpath("data/scpl_ios27_actions.json")
            .read_text(encoding="utf-8")
        )
        ids = [action["id"] for action in data["actions"]]

        self.assertEqual(len(ids), 282)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(set(ids), set(SOURCED_CATALOG))
        self.assertTrue(all(CATALOG[action_id]["availability"] == {"27": "observed"} for action_id in ids))

    def test_all_generated_schemas_emit_a_parseable_binary_plist(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated.shortcut"
            compile_plan(
                {
                    "version": 1,
                    "name": "Generated schema catalogue smoke check",
                    "actions": [{"id": action_id} for action_id in SOURCED_CATALOG],
                },
                output,
            )
            payload = output.read_bytes()
            document = plistlib.loads(payload)

        self.assertTrue(payload.startswith(b"bplist00"))
        self.assertEqual(len(document["WFWorkflowActions"]), len(SOURCED_CATALOG))

    def test_each_generated_parameter_key_matches_the_ios27_snapshot(self):
        catalog = json.loads(
            files("shortcutforge")
            .joinpath("data/action_catalog.json")
            .read_text(encoding="utf-8")
        )["actions"]
        data = json.loads(
            files("shortcutforge")
            .joinpath("data/scpl_ios27_actions.json")
            .read_text(encoding="utf-8")
        )

        for action in data["actions"]:
            observed_keys = {
                parameter["key"]
                for parameter in catalog[action["identifier"]].get("parameters", [])
            }
            source_keys = {parameter["key"] for parameter in action["parameters"]}
            self.assertTrue(source_keys.issubset(observed_keys), action["identifier"])
            self.assertEqual(action["ios27_parameter_evidence"], "matched")

        self.assertEqual(len(data["excluded_due_to_parameter_key_mismatch"]), 43)

    def test_generated_action_compiles_with_source_default(self):
        action_id = "add_to_up_next"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated.shortcut"
            compile_plan(
                {"version": 1, "name": "Generated schema", "actions": [{"id": action_id}]},
                output,
            )
            document = plistlib.loads(output.read_bytes())

        compiled = document["WFWorkflowActions"][0]
        self.assertEqual(
            compiled["WFWorkflowActionIdentifier"],
            "is.workflow.actions.addmusictoupnext",
        )
        self.assertEqual(
            compiled["WFWorkflowActionParameters"]["WFWhenToPlay"],
            "Next",
        )

    def test_generated_action_uses_exact_plist_parameter_keys(self):
        action_id = "add_to_up_next"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "generated.shortcut"
            compile_plan(
                {
                    "version": 1,
                    "name": "Generated parameter",
                    "actions": [{"id": action_id, "params": {"WFWhenToPlay": "Later"}}],
                },
                output,
            )
            compiled = plistlib.loads(output.read_bytes())["WFWorkflowActions"][0]

        self.assertEqual(
            compiled["WFWorkflowActionParameters"]["WFWhenToPlay"],
            "Later",
        )


if __name__ == "__main__":
    unittest.main()
