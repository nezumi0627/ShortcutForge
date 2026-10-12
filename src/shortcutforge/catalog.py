"""Searchable discovery catalog; entries are not all build-ready schemas."""
from __future__ import annotations

import json
from functools import lru_cache
from importlib.resources import files

_LABELS = {
    "en": {"title": "Apple Shortcuts action catalog", "selected": "Selected iOS version", "exact": "Exact-version identifiers", "candidate": "Discovery candidates (compatibility unknown)", "identifier": "Action identifier", "aliases": "Name / alias", "availability": "Evidence for selected iOS", "introduced": "Change history (source-reported)", "since": "Since", "change": "Change", "platform": "Platform note", "source": "Source", "observed": "Observed in iOS {os_version} Simulator snapshot", "unknown": "Unknown / unverified", "added": "Added", "removed": "Removed", "parameter": "Parameter change", "name_change": "Name / identifier change", "note": "Identifier presence alone does not verify parameters, import, or runtime behavior."},
    "ja": {"title": "Appleショートカット アクションカタログ", "selected": "選択したiOSバージョン", "exact": "この版で識別子を確認", "candidate": "検索候補（互換性は未確認）", "identifier": "アクション識別子", "aliases": "名称／別名", "availability": "選択したiOS版の根拠", "introduced": "変更履歴（出典に記載）", "since": "追加・変更時期", "change": "変更内容", "platform": "対応プラットフォームの注記", "source": "出典", "observed": "iOS {os_version} Simulatorスナップショットで確認", "unknown": "不明／未検証", "added": "追加", "removed": "削除", "parameter": "パラメータ変更", "name_change": "名称／識別子変更", "note": "識別子の記載だけでは、引数・読み込み・実行の互換性は確認できません。"},
}


def _markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


@lru_cache(maxsize=1)
def _version_changes() -> dict:
    return json.loads(files("shortcutforge").joinpath("data/version_changes.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _display_names() -> dict[str, str]:
    payload = json.loads(files("shortcutforge").joinpath("data/action_names.json").read_text(encoding="utf-8"))
    return payload["names"]


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, dict]:
    payload = json.loads(files("shortcutforge").joinpath("data/action_catalog.json").read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("actions"), dict):
        raise ValueError("unsupported packaged action catalog schema")
    return payload["actions"]


def catalog_entries(os_version: str | None = None, query: str | None = None) -> list[dict]:
    entries = load_catalog().values()
    names = _display_names()
    needle = (query or "").casefold()
    result = []
    for entry in entries:
        view = dict(entry)
        if entry["identifier"] in names:
            view["display_name"] = names[entry["identifier"]]
        if os_version:
            # Exact OS evidence is authoritative. For older versions, return
            # discovery candidates while keeping availability explicitly unknown.
            exact = any(e.get("os_version") == os_version and e.get("platform") == "iOS Simulator" for e in entry["evidence"])
            if os_version == "27" and not exact:
                continue
        searchable = [view["identifier"], view.get("category", ""), *view.get("aliases", [])]
        if view.get("display_name"):
            searchable.append(view["display_name"])
        if needle and needle not in " ".join(searchable).casefold():
            continue
        result.append(view)
    return sorted(result, key=lambda item: item["identifier"])


def render_catalog_markdown(os_version: str, language: str = "en", query: str | None = None) -> str:
    if os_version not in {"17", "18", "26", "27"}:
        raise ValueError("iOS version must be one of 17, 18, 26, or 27")
    if language not in _LABELS:
        raise ValueError("language must be en or ja")
    labels = _LABELS[language]
    entries = catalog_entries(os_version, query)
    exact_count = sum(any(e.get("os_version") == os_version and e.get("platform") == "iOS Simulator" for e in item["evidence"]) for item in entries)
    lines = [f"# {labels['title']} — iOS {os_version}", "", f"- **{labels['selected']}:** iOS {os_version}", f"- **{labels['exact']}:** {exact_count:,}", f"- **{labels['candidate']}:** {len(entries):,}", f"- {labels['note']}", ""]
    lines.extend([f"## {labels['introduced']}", "", f"| {labels['since']} | {labels['aliases']} | {labels['change']} | {labels['platform']} | {labels['source']} |", "|---|---|---|---|---|"])
    for change in _version_changes()["changes"]:
        since = change["since"]
        if since == "27 beta":
            include = os_version == "27"
        else:
            include = int(since.split(".")[0]) <= int(os_version)
        if not include:
            continue
        name = change[f"name_{language}"]
        change_label = labels.get(change["change"], change["change"])
        platform_note = change.get(f"platform_{language}", change.get("platform", "—"))
        source = _version_changes()["sources"][change["source"]]
        lines.append(f"| iOS {since} | {_markdown_cell(name)} | {change_label} | {_markdown_cell(platform_note)} | [source]({source}) |")
    lines.extend(["", f"## {labels['candidate']}", "", f"| {labels['identifier']} | {labels['aliases']} | {labels['availability']} |", "|---|---|---|"])
    for item in entries:
        exact = any(e.get("os_version") == os_version and e.get("platform") == "iOS Simulator" for e in item["evidence"])
        status = labels["observed"].format(os_version=os_version) if exact else labels["unknown"]
        name = item.get("display_name") or ", ".join(item.get("aliases", [])[:2])
        lines.append(f"| `{_markdown_cell(item['identifier'])}` | {_markdown_cell(name)} | {status} |")
    return "\n".join(lines) + "\n"
