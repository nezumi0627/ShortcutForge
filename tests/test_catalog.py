import json
import io
import unittest
import tempfile
from pathlib import Path
from contextlib import redirect_stdout, redirect_stderr
from shortcutforge.cli import main
from shortcutforge.catalog import catalog_entries, load_catalog, render_catalog_markdown


class CatalogTests(unittest.TestCase):
    def test_catalog_has_source_evidence_and_exact_ios27_snapshot(self):
        catalog = load_catalog()
        self.assertGreater(len(catalog), 1000)
        for identifier, entry in catalog.items():
            self.assertEqual(entry["identifier"], identifier)
            self.assertTrue(entry["evidence"])
            self.assertTrue(all(item["source"] for item in entry["evidence"]))
        ios27 = catalog_entries(os_version="27")
        self.assertGreater(len(ios27), 1000)
        self.assertTrue(all(any(e.get("os_version") == "27" and e.get("platform") == "iOS Simulator" for e in a["evidence"]) for a in ios27))

    def test_unknown_versions_are_not_falsely_exact(self):
        for version in ("17", "18", "26"):
            entries = catalog_entries(os_version=version)
            self.assertTrue(entries)
            self.assertTrue(all(a["availability"].get(version, "unknown") in {"unknown", "observed"} for a in entries))

    def test_search_and_alias_catalog_are_separate(self):
        self.assertTrue(catalog_entries(query="notification"))
        self.assertTrue(json.loads(json.dumps(load_catalog())))

    def test_cli_filters_by_os_and_query(self):
        output = io.StringIO()
        with redirect_stdout(output):
            import sys
            old = sys.argv
            try:
                sys.argv = ["shortcutforge", "actions", "list", "--os", "27", "--query", "calendar", "--format", "json"]
                self.assertEqual(main(), 0)
            finally:
                sys.argv = old
        rows = json.loads(output.getvalue())
        self.assertTrue(rows)
        self.assertTrue(all("calendar" in item["identifier"].casefold() or "calendar" in item.get("category", "").casefold() or "calendar" in item.get("display_name", "").casefold() or any("calendar" in a.casefold() for a in item.get("aliases", [])) for item in rows))

    def test_markdown_has_selected_version_language_and_version_changes(self):
        en = render_catalog_markdown("26", "en", query="battery")
        ja = render_catalog_markdown("27", "ja", query="calendar")
        self.assertIn("iOS 26", en)
        self.assertIn("iOS 26.4 | Set Battery Charge Limit | Added", en)
        self.assertIn("iOS 27", ja)
        self.assertIn("変更履歴", ja)
        self.assertIn("iOS 27 Simulator", ja)
        self.assertIn("iOSでの提供は未確認", ja)

    def test_cli_supports_markdown_and_language(self):
        output = io.StringIO()
        with redirect_stdout(output):
            import sys
            old = sys.argv
            try:
                sys.argv = ["shortcutforge", "actions", "list", "--os", "27", "--lang", "ja", "--format", "markdown", "--query", "calendar"]
                self.assertEqual(main(), 0)
            finally:
                sys.argv = old
        self.assertIn("iOS 27", output.getvalue())
        self.assertIn("識別子", output.getvalue())

    def test_cli_requires_target_ios_version_and_defaults_to_markdown(self):
        error = io.StringIO()
        with redirect_stderr(error):
            import sys
            old = sys.argv
            try:
                sys.argv = ["shortcutforge", "actions", "list"]
                with self.assertRaises(SystemExit):
                    main()
            finally:
                sys.argv = old
        self.assertIn("--os", error.getvalue())
        output = io.StringIO()
        with redirect_stdout(output):
            import sys
            old = sys.argv
            try:
                sys.argv = ["shortcutforge", "actions", "list", "--os", "17", "--query", "notification"]
                self.assertEqual(main(), 0)
            finally:
                sys.argv = old
        self.assertTrue(output.getvalue().startswith("# Apple Shortcuts action catalog — iOS 17"))

    def test_cli_writes_version_selected_markdown_file(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "ios26.ja.md"
            output = io.StringIO()
            with redirect_stdout(output):
                import sys
                old = sys.argv
                try:
                    sys.argv = ["shortcutforge", "actions", "list", "--os", "26", "--lang", "ja", "--format", "markdown", "--output", str(target), "--query", "battery"]
                    self.assertEqual(main(), 0)
                finally:
                    sys.argv = old
            self.assertTrue(target.exists())
            self.assertIn("iOS 26", target.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
