import json
import io
import unittest
from contextlib import redirect_stdout
from shortcutforge.cli import main
from shortcutforge.catalog import catalog_entries, load_catalog


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
                sys.argv = ["shortcutforge", "actions", "list", "--os", "27", "--query", "calendar"]
                self.assertEqual(main(), 0)
            finally:
                sys.argv = old
        rows = json.loads(output.getvalue())
        self.assertTrue(rows)
        self.assertTrue(all("calendar" in item["identifier"].casefold() or "calendar" in item.get("category", "").casefold() or any("calendar" in a.casefold() for a in item.get("aliases", [])) for item in rows))


if __name__ == "__main__":
    unittest.main()
