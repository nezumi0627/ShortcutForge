# Architecture

ShortcutForge keeps natural-language interpretation outside the Python package. An AI harness or human author creates a JSON plan; Python performs deterministic validation, compilation, and inspection. This avoids an LLM dependency and makes plans reviewable and hand-editable.

## Data flow

```text
Natural-language request (optional)
        │ interpreted by a person or AI harness
        ▼
Version 1 JSON plan ──► loader ──► validator ──► binary plist compiler
                                              │
Existing .shortcut ──────────────────────────┴──► read-only inspector

Action research ──► evidence catalog ──► version-filtered CLI / Markdown
```

The CLI is a thin adapter around package operations. `ir.py` loads plan JSON, `validator.py` checks supported semantics and safe plist value types, `compiler.py` writes a binary plist, and `parser.py` inspects an existing workflow without executing it. `actions.py` is the intentionally small build-time schema. `catalog.py` exposes the larger, evidence-oriented discovery index; discovery entries do not automatically become compilable actions.

## Core design decisions

### Keep planning data explicit

Version 1 plans are ordinary JSON with readable action IDs or exact raw Apple identifiers. Named IDs map to documented parameter keys. Raw actions preserve user-supplied parameter dictionaries but receive only structural checks. This supports manual authoring while avoiding claims that an incomplete catalog is a full Apple schema.

### Separate catalog evidence from compiler support

The discovery catalog is useful for research and manual authoring. It tracks version and provenance evidence, including unknown availability. The small compiler schema lists only actions ShortcutForge currently knows how to serialize. A catalog hit alone is not approval to compile an action.

### Keep the core dependency-light

Python standard-library modules handle JSON, CLI parsing, plist serialization, and process invocation. GitHub CLI (`gh`) is an external executable needed only by signing orchestration. The package does not contact an AI service.

### Treat signing as an optional external operation

The signing client dispatches a GitHub Actions workflow; Apple's `shortcuts sign` is run on macOS. Live testing showed that GitHub-hosted macOS requires iCloud sign-in and fails in the current configuration. The build output is unsigned; signing is required before file import into Shortcuts on iPhone/iPad. See [signing validation](signing-validation.md) and the [security model](security.md).

## Compatibility boundaries

- A valid binary plist is a serialization result, not proof of import or runtime behavior.
- The named compiler actions are currently `current_date`, `text`, `notify`, `speak`, and `open_url`.
- Variables/output references apply to the existing linear plan. Conditional and repeat blocks and calendar implementation are not supported.
- The version catalog is an evidence index, not a complete Apple-maintained API catalog.
- No physical iPhone import/runtime check has been completed; iOS 27 import remains unverified.

See the [JSON plan format](json-plan-format.md), [catalog coverage](action-catalog-sources.md), and [known limitations](../README.md#known-limitations).
