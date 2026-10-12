"""Searchable discovery catalog; entries are not all build-ready schemas."""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, dict]:
    payload = json.loads(files("shortcutforge").joinpath("data/action_catalog.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("actions"), dict):
        raise ValueError("unsupported packaged action catalog schema")
    return payload["actions"]


def catalog_entries(os_version: str | None = None, query: str | None = None) -> list[dict]:
    entries = load_catalog().values()
    needle = (query or "").casefold()
    result = []
    for entry in entries:
        if os_version:
            # Exact OS evidence is authoritative. For older versions, return
            # discovery candidates while keeping availability explicitly unknown.
            exact = any(e.get("os_version") == os_version and e.get("platform") == "iOS Simulator" for e in entry["evidence"])
            if os_version == "27" and not exact:
                continue
        if needle and needle not in " ".join([entry["identifier"], entry.get("category", ""), *entry.get("aliases", [])]).casefold():
            continue
        result.append(entry)
    return sorted(result, key=lambda item: item["identifier"])
