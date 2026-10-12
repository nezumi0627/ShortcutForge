# ShortcutForge Agent Guide

This file is the source of truth for repository-wide work. Read it before editing code, catalog data, workflows, or documentation.

## Mission and status

ShortcutForge is a Python 3.11+ CLI and harness-neutral Skill for turning typed JSON plans into Apple Shortcuts binary plists. AI harnesses interpret user intent; Python validates and compiles deterministically. The repository is public and is also configured as a GitHub template.

The project does **not** claim general Apple Shortcuts compatibility. Only five convenience actions are compiled by name (`current_date`, `text`, `notify`, `speak`, `open_url`). Conditional/repeat compilation and calendar support are not implemented. GitHub-hosted macOS signing failed because Apple requires an iCloud-authenticated environment. No iPhone import/runtime verification has been completed; iOS 27 import is unverified. Keep all these distinctions accurate in every user-facing document.

## Architecture

- `src/shortcutforge/ir.py`: version 1 JSON plan loading and structural checks.
- `src/shortcutforge/validator.py`: action, parameter, plist-value, and output-reference validation.
- `src/shortcutforge/compiler.py`: validated plan to binary plist.
- `src/shortcutforge/parser.py`: read-only plist inspection.
- `src/shortcutforge/actions.py`: small build-time action schema.
- `src/shortcutforge/catalog.py` and `data/`: versioned discovery index, evidence, names, and localized catalog rendering.
- `src/shortcutforge/signing.py`: GitHub CLI workflow dispatch, polling, and artifact download.
- `skills/shortcutforge/`: harness instructions; natural-language reasoning stays in the invoking AI.
- `.github/workflows/`: tests and optional signing/artifact workflows.
- `docs/`: user references, architecture, security, evidence, and contribution process.

Keep modules focused. Use the Python standard library unless a concrete project need justifies a dependency. Public Python APIs must be typed, documented where non-obvious, and covered by tests. Preserve compatibility wrappers when changing established interfaces unless the change is explicitly breaking.

## Coding and data conventions

- Support Python 3.11+. Use clear names, type hints, pathlib, small functions, and idiomatic error handling.
- Treat JSON plans, plist files, catalog contributions, workflow inputs, and downloaded artifacts as untrusted.
- Reject malformed or unsupported input before producing output. Never silently guess Apple serialization details.
- Separate action identifier observation, parameter evidence, OS availability, and runtime verification. Unknown means unknown.
- Preserve source URLs, source dates/versions, provenance, and required license notices for catalog data.
- Do not claim that plist validity implies import or execution success.
- Keep `en` and `ja` catalog documentation aligned when changing user-visible catalog behavior.

## JSON and action rules

The plan format is versioned JSON (`version: 1`) with a non-empty `name` and ordered `actions`. Each action uses exactly one of a known readable `id` or an explicit Apple `identifier`; `params` is an object and `as` optionally names an output. Consult `docs/json-plan-format.md` before changing this contract.

Add a named action only when its exact identifier, accepted parameters, required/default values, and input/output behavior are evidenced. Add validation and a focused fixture/test. Raw identifiers receive structural plist checks only; do not imply that ShortcutForge knows their schema or iOS availability. Do not implement control flow without an evidenced serialization model and tests.

## Version catalog

Callers must select iOS 17, 18, 26, or 27. The API models these as `IOSVersion`; use the catalog API (`ActionCatalog`) for new Python integrations. Keep the compatibility functions in `catalog.py` intact unless there is a deliberate migration. Version-filtered results describe the evidence available for that version, not a guarantee that an action exists or works on-device.

## Tests and quality gates

Run from the repository root:

```sh
python -m unittest discover -s tests -v
```

For an uninstalled `src` layout, set `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH='src'`). Also run `python -m compileall -q src` and `git diff --check` for code changes. Tests using mocks do not count as live Apple or GitHub signing validation. State exactly what was and was not verified.

## GitHub Actions and security

- Use least workflow permissions, bounded timeouts, concurrency controls where needed, and short artifact retention.
- Never print shortcut payloads, tokens, credentials, secret values, or personal data. Do not commit `.shortcut` files, generated payloads, local credentials, or user data.
- Do not assume a repository secret or Actions artifact remains private after the repository is public. Review workflow inputs, triggers, logs, permissions, and retention before modifying signing or publishing behavior.
- The current signing workflow is not operational on GitHub-hosted macOS without iCloud authentication. Do not claim otherwise or silently substitute a third-party signer.
- Public pull request workflows must not receive secrets. Treat PR source, catalog entries, filenames, and workflow_dispatch inputs as untrusted.
- Template-created repositories must not depend on source-repository secrets or inherit credentials. Provide explicit setup instructions instead.

## Documentation and contribution rules

Update README(s), the relevant docs, catalog notes, and Skill instructions whenever a user-facing command, JSON field, API, support claim, or workflow changes. Keep English and Japanese entry points consistent. Put the canonical user docs in `docs/README.md`; explain design rationale in `docs/architecture.md` and trust boundaries in `docs/security.md`.

Catalog corrections and additions are welcome. A useful PR includes the exact identifier, target iOS version/build and device or simulator, source/evidence, observed parameter keys where available, and whether the action was imported or run. Do not upgrade an evidence claim beyond what was actually tested.

## Agent operating constraints

- Follow the user's requested scope and this guide; do not claim unfinished features are complete.
- Inspect changes for generated files, secrets, personal content, unsupported compatibility claims, and stale docs before committing.
- Avoid unrelated refactors and new dependencies.
- Never change repository visibility, delete data, or publish an artifact unless the user explicitly requested it in the current task.
