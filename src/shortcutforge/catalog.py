"""Typed API for the sourced Apple Shortcuts action discovery catalog."""
from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from importlib.resources import files
from types import MappingProxyType
from typing import Any


class IOSVersion(StrEnum):
    """iOS versions currently represented by the catalog interface."""

    IOS_17 = "17"
    IOS_18 = "18"
    IOS_26 = "26"
    IOS_27 = "27"

    @classmethod
    def parse(cls, value: IOSVersion | str | int) -> IOSVersion:
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower().removeprefix("ios").strip()
        try:
            return cls(normalized)
        except ValueError as exc:
            supported = ", ".join(version.value for version in cls)
            raise ValueError(f"unsupported iOS version {value!r}; choose {supported}") from exc


class CatalogLanguage(StrEnum):
    """Supported interface languages for generated catalog documents."""

    ENGLISH = "en"
    JAPANESE = "ja"

    @classmethod
    def parse(cls, value: CatalogLanguage | str) -> CatalogLanguage:
        if isinstance(value, cls):
            return value
        try:
            return cls(str(value).strip().lower())
        except ValueError as exc:
            raise ValueError("language must be 'en' or 'ja'") from exc


class ActionAvailability(StrEnum):
    """What this catalog can say about an action on a requested iOS release."""

    OBSERVED = "observed"
    UNKNOWN = "unknown"
    NOT_IN_CATALOG = "not_in_catalog"


@dataclass(frozen=True, slots=True)
class ActionEvidence:
    source: str
    url: str | None = None
    kind: str | None = None
    platform: str | None = None
    platforms: tuple[str, ...] = ()
    os_version: str | None = None
    observed_at: str | None = None
    runtime: str | None = None
    build: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ActionEvidence:
        return cls(
            source=str(data["source"]),
            url=data.get("url"),
            kind=data.get("kind"),
            platform=data.get("platform"),
            platforms=tuple(data.get("platforms", ())),
            os_version=data.get("os_version"),
            observed_at=data.get("observed_at"),
            runtime=data.get("runtime"),
            build=data.get("build"),
        )

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"source": self.source}
        for name in ("url", "kind", "platform", "os_version", "observed_at", "runtime", "build"):
            value = getattr(self, name)
            if value is not None:
                result[name] = value
        if self.platforms:
            result["platforms"] = list(self.platforms)
        return result


@dataclass(frozen=True, slots=True)
class ActionParameter:
    """Observed input parameter metadata; not a guarantee of build support."""

    key: str
    name: str | None = None
    value_type: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ActionParameter:
        return cls(
            key=str(data["key"]),
            name=data.get("name"),
            value_type=data.get("type"),
        )

    def to_dict(self) -> dict[str, str]:
        result = {"key": self.key}
        if self.name is not None:
            result["name"] = self.name
        if self.value_type is not None:
            result["type"] = self.value_type
        return result


@dataclass(frozen=True, slots=True)
class CatalogAction:
    identifier: str
    availability: Mapping[str, str]
    evidence: tuple[ActionEvidence, ...]
    aliases: tuple[str, ...] = ()
    category: str | None = None
    display_name: str | None = None
    parameters: tuple[ActionParameter, ...] = ()
    parameter_evidence: Mapping[str, Any] | None = None

    @classmethod
    def from_dict(
        cls, data: Mapping[str, Any], *, display_name: str | None = None
    ) -> CatalogAction:
        parameter_evidence = data.get("parameter_evidence")
        return cls(
            identifier=str(data["identifier"]),
            availability=MappingProxyType(dict(data.get("availability", {}))),
            evidence=tuple(
                ActionEvidence.from_dict(item)
                for item in data.get("evidence", ())
            ),
            aliases=tuple(data.get("aliases", ())),
            category=data.get("category"),
            display_name=display_name,
            parameters=tuple(
                ActionParameter.from_dict(item)
                for item in data.get("parameters", ())
            ),
            parameter_evidence=(
                MappingProxyType(dict(parameter_evidence))
                if parameter_evidence
                else None
            ),
        )

    def is_observed_on(self, version: IOSVersion | str | int) -> bool:
        target = IOSVersion.parse(version)
        return any(
            evidence.os_version == target.value and evidence.platform == "iOS Simulator"
            for evidence in self.evidence
        )

    def matches(self, query: str | None) -> bool:
        if not query:
            return True
        searchable = (self.identifier, self.category or "", self.display_name or "", *self.aliases)
        needle = query.casefold()
        return any(needle in value.casefold() for value in searchable)

    def to_dict(self, *, include_display_name: bool = True) -> dict[str, Any]:
        result: dict[str, Any] = {
            "identifier": self.identifier,
            "availability": dict(self.availability),
            "evidence": [item.to_dict() for item in self.evidence],
            "aliases": list(self.aliases),
        }
        if self.category is not None:
            result["category"] = self.category
        if include_display_name and self.display_name is not None:
            result["display_name"] = self.display_name
        if self.parameters:
            result["parameters"] = [item.to_dict() for item in self.parameters]
        if self.parameter_evidence is not None:
            result["parameter_evidence"] = dict(self.parameter_evidence)
        return result


@dataclass(frozen=True, slots=True)
class VersionChange:
    since: str
    baseline: str
    source: str
    name_en: str
    name_ja: str
    change: str
    platform_en: str | None = None
    platform_ja: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> VersionChange:
        return cls(
            since=str(data["since"]),
            baseline=str(data["baseline"]),
            source=str(data["source"]),
            name_en=str(data["name_en"]),
            name_ja=str(data["name_ja"]),
            change=str(data["change"]),
            platform_en=data.get("platform"),
            platform_ja=data.get("platform_ja"),
        )

    def applies_through(self, version: IOSVersion) -> bool:
        if self.since == "27 beta":
            return version is IOSVersion.IOS_27
        return int(self.since.split(".", maxsplit=1)[0]) <= int(version.value)

    def localized_name(self, language: CatalogLanguage) -> str:
        return self.name_ja if language is CatalogLanguage.JAPANESE else self.name_en

    def localized_platform(self, language: CatalogLanguage) -> str:
        if language is CatalogLanguage.JAPANESE:
            return self.platform_ja or self.platform_en or "—"
        return self.platform_en or "—"


_LABELS = {
    CatalogLanguage.ENGLISH: {
        "title": "Apple Shortcuts action catalog",
        "selected": "Selected iOS version",
        "exact": "Exact-version identifiers",
        "candidate": "Discovery candidates (compatibility unknown)",
        "identifier": "Action identifier",
        "aliases": "Name / alias",
        "availability": "Evidence for selected iOS",
        "introduced": "Change history (source-reported)",
        "since": "Since",
        "baseline": "Compared with",
        "change": "Change",
        "platform": "Platform note",
        "source": "Source",
        "observed": "Observed in iOS {os_version} Simulator snapshot",
        "unknown": "Unknown / unverified",
        "added": "Added",
        "removed": "Removed",
        "parameter": "Parameter change",
        "name_change": "Name / identifier change",
        "note": (
            "Identifier presence alone does not verify parameters, import, "
            "or runtime behavior."
        ),
    },
    CatalogLanguage.JAPANESE: {
        "title": "Appleショートカット アクションカタログ",
        "selected": "選択したiOSバージョン",
        "exact": "この版で識別子を確認",
        "candidate": "検索候補（互換性は未確認）",
        "identifier": "アクション識別子",
        "aliases": "名称／別名",
        "availability": "選択したiOS版の根拠",
        "introduced": "変更履歴（出典に記載）",
        "since": "追加・変更時期",
        "baseline": "比較元",
        "change": "変更内容",
        "platform": "対応プラットフォームの注記",
        "source": "出典",
        "observed": "iOS {os_version} Simulatorスナップショットで確認",
        "unknown": "不明／未検証",
        "added": "追加",
        "removed": "削除",
        "parameter": "パラメータ変更",
        "name_change": "名称／識別子変更",
        "note": "識別子の記載だけでは、引数・読み込み・実行の互換性は確認できません。",
    },
}


def _markdown_cell(value: str) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _read_json(filename: str) -> dict[str, Any]:
    return json.loads(files("shortcutforge").joinpath("data", filename).read_text(encoding="utf-8"))


@dataclass(frozen=True, slots=True, init=False)
class ActionCatalog:
    """Immutable, version-aware view over the packaged action evidence."""

    _actions: Mapping[str, CatalogAction]
    _changes: tuple[VersionChange, ...]
    _change_sources: Mapping[str, str]

    def __init__(
        self,
        actions: Iterable[CatalogAction],
        *,
        changes: Iterable[VersionChange] = (),
        change_sources: Mapping[str, str] | None = None,
    ) -> None:
        action_list = tuple(actions)
        action_map = {action.identifier: action for action in action_list}
        if len(action_map) != len(action_list):
            raise ValueError("catalog contains duplicate action identifiers")
        object.__setattr__(self, "_actions", MappingProxyType(action_map))
        object.__setattr__(self, "_changes", tuple(changes))
        object.__setattr__(self, "_change_sources", MappingProxyType(dict(change_sources or {})))

    @classmethod
    def from_package(cls) -> ActionCatalog:
        catalog_data = _read_json("action_catalog.json")
        if (
            catalog_data.get("schema_version") != 1
            or not isinstance(catalog_data.get("actions"), dict)
        ):
            raise ValueError("unsupported packaged action catalog schema")

        name_data = _read_json("action_names.json")
        if name_data.get("schema_version") != 1 or not isinstance(name_data.get("names"), dict):
            raise ValueError("unsupported packaged action-name schema")

        change_data = _read_json("version_changes.json")
        if (
            change_data.get("schema_version") != 1
            or not isinstance(change_data.get("changes"), list)
        ):
            raise ValueError("unsupported packaged version-change schema")

        names = name_data["names"]
        actions = (
            CatalogAction.from_dict(raw, display_name=names.get(identifier))
            for identifier, raw in catalog_data["actions"].items()
        )
        return cls(
            actions,
            changes=(VersionChange.from_dict(item) for item in change_data["changes"]),
            change_sources=change_data.get("sources", {}),
        )

    def get(self, identifier: str) -> CatalogAction | None:
        return self._actions.get(identifier)

    def list_actions(
        self,
        version: IOSVersion | str | int,
        *,
        query: str | None = None,
    ) -> tuple[CatalogAction, ...]:
        return self._filter_actions(IOSVersion.parse(version), query)

    def list_all_actions(self, *, query: str | None = None) -> tuple[CatalogAction, ...]:
        """List discovery records without asserting a target iOS release."""
        return self._filter_actions(None, query)

    def _filter_actions(
        self,
        version: IOSVersion | None,
        query: str | None,
    ) -> tuple[CatalogAction, ...]:
        actions = (
            action for action in self._actions.values()
            if (
                version is None
                or version is not IOSVersion.IOS_27
                or action.is_observed_on(version)
            )
            and action.matches(query)
        )
        return tuple(sorted(actions, key=lambda action: action.identifier))

    def get_availability(
        self, identifier: str, version: IOSVersion | str | int
    ) -> ActionAvailability:
        target = IOSVersion.parse(version)
        action = self.get(identifier)
        if action is None:
            return ActionAvailability.NOT_IN_CATALOG
        if action.is_observed_on(target):
            return ActionAvailability.OBSERVED
        return ActionAvailability.UNKNOWN

    def render_markdown(
        self,
        version: IOSVersion | str | int,
        language: CatalogLanguage | str = CatalogLanguage.ENGLISH,
        *,
        query: str | None = None,
    ) -> str:
        target = IOSVersion.parse(version)
        locale = CatalogLanguage.parse(language)
        labels = _LABELS[locale]
        actions = self.list_actions(target, query=query)
        exact_count = sum(action.is_observed_on(target) for action in actions)
        lines = [
            f"# {labels['title']} — iOS {target.value}", "",
            f"- **{labels['selected']}:** iOS {target.value}",
            f"- **{labels['exact']}:** {exact_count:,}",
            f"- **{labels['candidate']}:** {len(actions):,}",
            f"- {labels['note']}", "",
            f"## {labels['introduced']}", "",
            f"| {labels['since']} | {labels['baseline']} | {labels['aliases']} "
            f"| {labels['change']} | {labels['platform']} | {labels['source']} |",
            "|---|---|---|---|---|---|",
        ]
        for change in self._changes:
            if not change.applies_through(target):
                continue
            change_label = labels.get(change.change, change.change)
            source_url = self._change_sources.get(change.source, "")
            source_cell = f"[source]({source_url})" if source_url else "—"
            lines.append(
                f"| iOS {change.since} | {change.baseline} "
                f"| {_markdown_cell(change.localized_name(locale))} | {change_label} "
                f"| {_markdown_cell(change.localized_platform(locale))} | {source_cell} |"
            )

        lines.extend([
            "", f"## {labels['candidate']}", "",
            f"| {labels['identifier']} | {labels['aliases']} | {labels['availability']} |",
            "|---|---|---|",
        ])
        for action in actions:
            status = (
                labels["observed"].format(os_version=target.value)
                if action.is_observed_on(target)
                else labels["unknown"]
            )
            name = action.display_name or ", ".join(action.aliases[:2])
            lines.append(
                f"| `{_markdown_cell(action.identifier)}` "
                f"| {_markdown_cell(name)} | {status} |"
            )
        return "\n".join(lines) + "\n"

    def to_dict(self, *, include_display_names: bool = False) -> dict[str, dict[str, Any]]:
        return {
            identifier: action.to_dict(include_display_name=include_display_names)
            for identifier, action in self._actions.items()
        }


@lru_cache(maxsize=1)
def get_default_catalog() -> ActionCatalog:
    """Load the packaged catalog once; the returned catalog is immutable."""
    return ActionCatalog.from_package()


def load_catalog() -> dict[str, dict[str, Any]]:
    """Return a fresh plain-dict snapshot for existing callers and JSON output."""
    return get_default_catalog().to_dict()


def catalog_entries(
    os_version: IOSVersion | str | int | None = None,
    query: str | None = None,
) -> list[dict[str, Any]]:
    catalog = get_default_catalog()
    actions = (
        catalog.list_all_actions(query=query)
        if os_version is None
        else catalog.list_actions(os_version, query=query)
    )
    return [
        action.to_dict(include_display_name=True)
        for action in actions
    ]


def render_catalog_markdown(
    os_version: IOSVersion | str | int,
    language: CatalogLanguage | str = CatalogLanguage.ENGLISH,
    query: str | None = None,
) -> str:
    return get_default_catalog().render_markdown(os_version, language, query=query)
