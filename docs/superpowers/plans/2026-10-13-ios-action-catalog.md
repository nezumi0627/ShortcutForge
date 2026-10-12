# iOS Shortcuts Action Catalog Implementation Plan

> **For agentic workers:** Use this plan task-by-task; keep each catalog claim linked to source evidence.

**Goal:** Expand ShortcutForge's searchable action catalog with action IDs and available metadata for iOS 17, 18, 26, and 27, while exposing the evidence strength and avoiding invented version compatibility.

**Architecture:** Store a normalized, versioned JSON catalog inside the Python package. Preserve source/provenance per record; merge independent snapshots without treating unknown availability as universal support. Keep the existing raw-action escape hatch for parameters and behaviors not sufficiently documented.

**Tech Stack:** Python 3.11+, JSON, `plistlib`, `unittest`; no runtime network access or new dependencies.

**Spec:** User request in conversation (catalog research across iOS 17, 18, 26, and 27).

## Global Constraints

- Keep Python 3.11+ and standard-library-first.
- Do not invent exact iOS availability from unversioned catalogs.
- Distinguish identifier discovery from verified parameter serialization and runtime behavior.
- Preserve source URLs, snapshot dates, and upstream license notices for bundled datasets.
- Do not copy non-open licensed descriptions or datasets without permission.

## Review Focus

- The same action appears in multiple OS snapshots; merge provenance without losing version evidence.
- A minimum OS value is heuristic or absent; show `unknown`, not a guessed version range.
- An action ID exists but its parameter schema is incomplete; do not claim it is build-ready.
- Dataset includes macOS-only or third-party actions; filter/label platform and origin.
- Search/list commands return useful, deterministic output across all target versions.

---

### Task 1: Catalog data and provenance

**Files:**
- Create: `src/shortcutforge/data/action_catalog.json`
- Create: `src/shortcutforge/data/NOTICE.md`
- Modify: `pyproject.toml`
- Test: `tests/test_catalog.py`

**Interfaces:** `load_catalog() -> dict[str, dict]` returns entries keyed by Apple action identifier; each entry records `identifier`, optional `name`/`category`, `platforms`, `availability`, optional observed parameter metadata, and source evidence.

- [x] Add failing tests for source attribution, per-version evidence and exact iOS 27 filtering.
- [x] Run the catalog tests and confirm the expected initial failure.
- [x] Normalize licensed upstream snapshots and public action references into the JSON catalog; preserve source metadata and notices.
- [x] Mark iOS 17/18/26 availability unknown because exact snapshots were not found.
- [x] Package the JSON data with the Python distribution and run tests.

### Task 2: Catalog lookup and CLI

**Files:**
- Modify: `src/shortcutforge/actions.py`
- Modify: `src/shortcutforge/cli.py`
- Test: `tests/test_catalog.py`

**Interfaces:** `CATALOG` remains the build-time action mapping for curated parameter schemas. `actions list` gains optional target OS filtering and search; raw catalog entries remain discoverable without being falsely promoted to fully parameterized builders.

- [x] Add a failing CLI test for OS and query filtering.
- [x] Run the focused tests and confirm failure.
- [x] Implement deterministic lookup over the packaged JSON, retaining current aliases and schemas.
- [x] Run the full tests and representative queries on all four targets.

### Task 3: Documentation and evidence report

**Files:**
- Modify: `README.md`
- Modify: `skills/shortcutforge/SKILL.md`
- Create: `docs/action-catalog-sources.md`

- [x] Document what an ID listing proves and does not prove.
- [x] Document iOS 17/18/26 evidence gaps and a reproducible device-export refresh path.
- [x] Document sources, license notices, snapshot dates, and catalog counts.
- [x] Run tests, inspect generated catalog counts, and check the final diff.

