---
name: shortcutforge
description: Create, validate, inspect, and sign Apple Shortcuts from natural-language requests using the local ShortcutForge CLI.
---

# ShortcutForge

Use the harness's reasoning to translate the user's intent into a version 1 JSON plan. ShortcutForge performs deterministic schema validation and binary plist generation; it does not call an LLM.

## Procedure

1. Ask only for details needed to resolve meaningful ambiguity (for example, which calendar or notification text).
2. Check available actions with `shortcutforge actions list`. Prefer readable catalog IDs and parameter names. Apple plist parameter keys are also accepted. For an uncatalogued action, use `identifier` with an exact Apple action identifier and include its raw parameter dictionary, sourced from a real shortcut or trusted reference.
3. Write the plan JSON to a temporary file outside the repository. Do not include passwords, tokens, or other secrets.
4. Run `shortcutforge build plan.json -o result.shortcut`, then `shortcutforge validate result.shortcut` and `shortcutforge inspect result.shortcut`.
5. Run `shortcutforge sign result.shortcut` only when the user requests a shareable signed shortcut and the private GitHub repository is configured. Signing sends the shortcut to Apple for validation and transmits its base64 payload as private GitHub workflow input; do not use it for sensitive personal data.
6. Give the user the resulting file path and clearly state any unsupported or unverified behavior.

## Plan format

```json
{"version":1,"name":"Notify current time","actions":[{"id":"current_date","as":"now"},{"id":"notify","params":{"text":{"ref":"now"}}}]}
```

An action may use either a readable catalog `id` or a raw Apple `identifier`, never both. Catalog parameter names and Apple plist parameter keys are both accepted. Raw actions pass through JSON-compatible plist values and receive basic structural validation only; ShortcutForge cannot verify that iOS recognizes them or that their parameters are complete. An action may have an `as` output name; catalogued parameters accept `{"ref":"name"}` references. Do not pass the same parameter using both names.

Raw Apple example:

```json
{"version":1,"name":"Notify","actions":[{"identifier":"is.workflow.actions.notification","params":{"WFNotificationActionBody":"Hello","WFNotificationActionSound":false}}]}
```

## Examples

```sh
shortcutforge actions list
shortcutforge build plan.json -o Hello.shortcut
shortcutforge validate Hello.shortcut
shortcutforge inspect Hello.shortcut
shortcutforge sign Hello.shortcut
```

## Installation

Install this repository's Python package with `python -m pip install .`. For Codex, install or link `skills/shortcutforge` into the harness skill directory. For Claude Code, link the same directory under `.claude/skills/shortcutforge`. The skill is harness-neutral and requires no model API key.
