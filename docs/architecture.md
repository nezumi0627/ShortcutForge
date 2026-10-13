# Architecture

ShortcutForge keeps natural-language interpretation outside the Python package. An AI harness or human author creates either a typed JSON plan or Cherri source; the selected compiler builds an unsigned workflow. This avoids an LLM dependency and keeps both source formats reviewable and hand-editable.

## Data flow

```text
Natural-language request (optional)
        │ interpreted by a person or AI harness
        ├──► Version 1 JSON ──► loader ──► validator ──► Python plist compiler ──┐
        └──► Cherri source ──► external Cherri compiler (--skip-sign) ───────────┤
                                                                                ├─► unsigned .shortcut
Existing .shortcut ───────────────────────────► read-only inspector ────────────┘

Action research ──► evidence catalog ──► version-filtered CLI / Markdown
Unsigned .shortcut ──► explicit signer ──► signed artifact
```

The CLI is a thin adapter around package operations. `ir.py` loads plan JSON, `validator.py` checks supported semantics and safe plist value types, and `compiler.py` writes a binary plist. For `.cherri`, `cherri.py` invokes an optional executable, disables its signing, validates the returned plist, and atomically writes the requested output. `parser.py` inspects a workflow without executing it. `actions.py` is the intentionally small JSON build-time schema. `catalog.py` exposes the larger, evidence-oriented discovery index; discovery entries do not automatically become compilable actions.

## Core design decisions

### Keep planning data explicit

Version 1 plans are ordinary JSON with readable action IDs or exact raw Apple identifiers. Named IDs map to documented parameter keys. Raw actions preserve user-supplied parameter dictionaries but receive only structural checks. This supports manual authoring while avoiding claims that an incomplete catalog is a full Apple schema.

### Separate catalog evidence from compiler support

The discovery catalog is useful for research and manual authoring. It tracks version and provenance evidence, including unknown availability. The small compiler schema lists only actions ShortcutForge currently knows how to serialize. A catalog hit alone is not approval to compile an action.

### Keep the core dependency-light

Python standard-library modules handle JSON, CLI parsing, plist serialization, and process invocation. Cherri is an optional, separately installed executable used only for `.cherri` builds. The package does not contact an AI service.

### Treat signing as an explicit external operation

`shortcutforge sign` uses Shortcuty's keyless signing service by default and Shortcuty is the only enabled signer on Windows. On supported non-Windows hosts, `--via hubsign` selects RoutineHub HubSign and `--via macos` runs Apple's `shortcuts sign --mode anyone` locally. Other Windows signing approaches remain under research and are not exposed as working commands. GitHub Actions are reserved for CI and do not receive user shortcut files. The build output is unsigned; signing is required before file import into Shortcuts on iPhone/iPad. Remote signers receive the shortcut for signing. See [signing validation](signing-validation.md) and the [security model](security.md).

### Keep compiler guarantees distinct

The JSON compiler validates its versioned plan shape and its small named-action schema. Cherri owns parsing and language semantics for `.cherri`; ShortcutForge only controls invocation and checks that Cherri returned an unsigned plist with a workflow action list. Neither path proves the generated file imports or runs on a target iOS release.

## Compatibility boundaries

- A valid binary plist is a serialization result, not proof of import or runtime behavior.
- The named compiler actions are currently `current_date`, `text`, `notify`, `speak`, and `open_url`.
- The JSON compiler has no high-level conditional/repeat DSL. For code-first control flow, use the optional Cherri adapter and its [integration guide](cherri-integration.md).
- The version catalog is an evidence index, not a complete Apple-maintained API catalog.
- No physical iPhone import/runtime check has been completed; iOS 27 import remains unverified.

See the [JSON plan format](json-plan-format.md), [catalog coverage](action-catalog-sources.md), and [known limitations](../README.md#known-limitations).
