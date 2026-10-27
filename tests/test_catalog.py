import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from shortcutforge import ActionCatalog as PublicActionCatalog
from shortcutforge import IOSVersion as PublicIOSVersion
from shortcutforge.cli import main
from shortcutforge.catalog import (
    ActionAvailability,
    ActionCatalog,
    CatalogLanguage,
    IOSVersion,
    catalog_entries,
    load_catalog,
    render_catalog_markdown,
)


class CatalogTests(unittest.TestCase):
    def test_object_api_filters_actions_and_reports_version_evidence(self):
        catalog = ActionCatalog.from_package()
        actions = catalog.list_actions(IOSVersion.IOS_27, query="calendar")
        self.assertTrue(actions)
        self.assertIsInstance(actions, tuple)
        self.assertTrue(
            all(action.is_observed_on(IOSVersion.IOS_27) for action in actions)
        )
        self.assertEqual(
            catalog.get_availability(
                "is.workflow.actions.notification", IOSVersion.IOS_26
            ),
            ActionAvailability.UNKNOWN,
        )
        self.assertEqual(
            catalog.get_availability("missing.action", IOSVersion.IOS_27),
            ActionAvailability.NOT_IN_CATALOG,
        )
        with self.assertRaises(TypeError):
            actions[0].availability["26"] = "observed"

    def test_version_and_language_enums_parse_public_inputs(self):
        self.assertIs(IOSVersion.parse(26), IOSVersion.IOS_26)
        self.assertIs(CatalogLanguage.parse("ja"), CatalogLanguage.JAPANESE)
        with self.assertRaises(ValueError):
            IOSVersion.parse("25")
        self.assertIs(PublicActionCatalog, ActionCatalog)
        self.assertIs(PublicIOSVersion, IOSVersion)

    def test_catalog_has_source_evidence_and_exact_ios27_snapshot(self):
        catalog = load_catalog()
        self.assertGreater(len(catalog), 1000)
        for identifier, entry in catalog.items():
            self.assertEqual(entry["identifier"], identifier)
            self.assertTrue(entry["evidence"])
            self.assertTrue(all(item["source"] for item in entry["evidence"]))
        ios27 = catalog_entries(os_version="27")
        self.assertGreater(len(ios27), 1000)
        self.assertTrue(
            all(
                any(
                    evidence.get("os_version") == "27"
                    and evidence.get("platform") == "iOS Simulator"
                    for evidence in action["evidence"]
                )
                for action in ios27
            )
        )

    def test_unknown_versions_are_not_falsely_exact(self):
        for version in ("17", "18", "26"):
            entries = catalog_entries(os_version=version)
            self.assertTrue(entries)
            self.assertTrue(
                all(
                    action["availability"].get(version, "unknown")
                    in {"unknown", "observed"}
                    for action in entries
                )
            )

    def test_search_and_alias_catalog_are_separate(self):
        self.assertTrue(catalog_entries(query="notification"))
        self.assertTrue(json.loads(json.dumps(load_catalog())))

    def test_cli_filters_by_os_and_query(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(
                    [
                        "actions", "list", "--os", "27", "--query", "calendar",
                        "--format", "json",
                    ]
                ),
                0,
            )
        rows = json.loads(output.getvalue())
        self.assertTrue(rows)
        self.assertTrue(
            all(
                "calendar" in item["identifier"].casefold()
                or "calendar" in item.get("category", "").casefold()
                or "calendar" in item.get("display_name", "").casefold()
                or any("calendar" in alias.casefold() for alias in item.get("aliases", []))
                for item in rows
            )
        )

    def test_markdown_has_selected_version_language_and_version_changes(self):
        en = render_catalog_markdown("26", "en", query="battery")
        ja = render_catalog_markdown("27", "ja", query="calendar")
        self.assertIn("iOS 26", en)
        self.assertIn("iOS 26.4 | iOS 26.2 | Set Battery Charge Limit | Added", en)
        self.assertIn("iOS 27", ja)
        self.assertIn("変更履歴", ja)
        self.assertIn("iOS 27 Simulator", ja)
        self.assertIn("iOSでの提供は未確認", ja)

    def test_official_versioned_action_changes_appear_for_selected_ios(self):
        ios17 = render_catalog_markdown("17", "en")
        ios18 = render_catalog_markdown("18", "en")
        ios26 = render_catalog_markdown("26", "en")

        self.assertIn("Get Orientation", ios17)
        self.assertIn("Create Entry / Create Audio Entry / Search Entries (Journal)", ios18)
        self.assertIn("Create Image / Use Model / Writing Tools actions", ios26)

    def test_cli_supports_markdown_and_language(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(
                    [
                        "actions", "list", "--os", "27", "--lang", "ja",
                        "--format", "markdown", "--query", "calendar",
                    ]
                ),
                0,
            )
        self.assertIn("iOS 27", output.getvalue())
        self.assertIn("識別子", output.getvalue())

    def test_cli_requires_target_ios_version_and_defaults_to_markdown(self):
        error = io.StringIO()
        with redirect_stderr(error):
            with self.assertRaises(SystemExit):
                main(["actions", "list"])
        self.assertIn("--os", error.getvalue())
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(
                main(["actions", "list", "--os", "17", "--query", "notification"]),
                0,
            )
        self.assertTrue(output.getvalue().startswith("# Apple Shortcuts action catalog — iOS 17"))

    def test_cli_writes_version_selected_markdown_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "ios26.ja.md"
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            "actions", "list", "--os", "26", "--lang", "ja",
                            "--format", "markdown", "--output", str(target),
                            "--query", "battery",
                        ]
                    ),
                    0,
                )
            self.assertTrue(target.exists())
            self.assertIn("iOS 26", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
