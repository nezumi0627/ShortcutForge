# ShortcutForge Agent Guide

This is the repository's canonical instruction file. Read it before changing source, catalog data, workflows, Skills, examples, or docs. Keep claims consistent with the evidence and current implementation.

## Mission

ShortcutForge is a Python 3.11+ command-line toolkit and harness-neutral Skill for authoring Apple Shortcuts from typed JSON or optional Cherri source. A person or AI harness decides what the shortcut should do. ShortcutForge performs deterministic validation, compilation, inspection, and supported signing operations. It does not call an LLM.

The repository is public and configured as a GitHub template. Never assume secrets, credentials, private files, or signing access transfer to a template-derived repository.

## Current capability boundaries

- The built-in JSON compiler has 19 hand-curated schemas and 282 sourced generated schemas. The generated schemas are simulator-evidence candidates, not device-tested guarantees. See [named actions](docs/named-actions.md) for IDs, parameters, evidence, and limits. It does not implement high-level conditional or repeat builders.
- Raw JSON actions can carry exact Apple identifiers and parameters, but ShortcutForge only checks basic plist structure; it does not know whether iOS recognizes the action or parameters.
- `.cherri` input is delegated to a separately installed external Cherri executable. ShortcutForge always disables Cherri signing and validates the resulting plist. A Windows smoke test has compiled the included If/Repeat example, but this does not establish support for every Cherri feature or release.
- The action catalog is a versioned research/discovery index, not a full Apple schema or compiler registry. It supports iOS 17, 18, 26, and 27 with uneven evidence.
- A plist passing validation does not prove Shortcuts import or runtime success. No physical iPhone import/runtime test has been completed; iOS 27 import remains unverified.
- `build` produces unsigned files. A file intended for import into iPhone/iPad Shortcuts must be signed first.

Do not overstate any of these capabilities in code, docs, Skill instructions, examples, release notes, or user-facing reports.

## Signing and data handling

- `shortcutforge sign FILE` defaults to Shortcuty. On Windows, Shortcuty is the only enabled signer; reject HubSign and macOS signer selections with a clear error. Alternative Windows methods are research-only.
- Shortcuty uploads the complete workflow to its remote signing service. HubSign also receives the workflow and requires its API key/account access. Apple's macOS signer invokes Apple's `shortcuts sign` locally and sends a copy to Apple for validation.
- Disclose remote data transfer. Never submit a workflow containing private, secret, or sensitive data without user authorization.
- GitHub Actions are for CI only. Never use Actions to sign, upload, or transport user shortcut files.
- Do not add a signing route that stores shortcut content in repository history, CI logs, artifacts, or issue/PR comments.
- Keep credentials out of arguments, output, logs, source control, examples, and template content. Avoid printing compiler stderr if it can contain source or secrets.

See [signing validation](docs/signing-validation.md) and [security model](docs/security.md) for the fuller data-flow account.

## Architecture and ownership

- `src/shortcutforge/cli.py`: command parsing and orchestration; keep business rules in package modules.
- `src/shortcutforge/ir.py`: version 1 JSON loading and shape validation.
- `src/shortcutforge/validator.py`: action, parameter, plist-compatible value, and reference validation.
- `src/shortcutforge/compiler.py`: validated JSON plan to binary plist.
- `src/shortcutforge/parser.py`: read-only inspection of existing workflow plists.
- `src/shortcutforge/actions.py`: hand-curated and generated named-action compilation schemas.
- `src/shortcutforge/cherri.py`: optional external compiler adapter; no shell, signing disabled, bounded runtime, safe temporary output handling, plist validation.
- `src/shortcutforge/catalog.py` and `src/shortcutforge/data/`: versioned action discovery data, evidence, aliases, and localized Markdown rendering.
- `src/shortcutforge/signing.py`: supported signer integrations and response validation. Enforce platform restrictions in the CLI.
- `skills/shortcutforge/`: Codex/Claude Code usage instructions. Harness reasoning belongs to the caller, not Python.
- `.github/workflows/`: CI and repository maintenance only; no shortcut payload signing.
- `docs/`: canonical user, contributor, architecture, security, and evidence documentation.

Keep modules narrow and APIs typed. Prefer the Python standard library. Do not add an abstraction or dependency without a specific need.

## Input, compiler, and Cherri rules

- Treat JSON plans, plist files, catalog contributions, `.cherri` sources, filenames, and downloaded responses as untrusted.
- Reject malformed or unsupported input before final output is written. Avoid partial output on compiler failure.
- The JSON plan contract is versioned (`version: 1`) and documented in [JSON plan format](docs/json-plan-format.md). Preserve its validation guarantees.
- Add a hand-curated JSON action only when the exact identifier, accepted parameters, required/default values, and input/output behavior have evidence and focused tests. Generated catalog imports must retain source/license metadata, filter to version-observed identifiers, reject unsupported parameter serializers, and document provenance and limitations. Update [named actions](docs/named-actions.md), [JSON plan format](docs/json-plan-format.md), and both READMEs when the set changes.
- Raw action identifiers get structural checks only. Do not silently infer parameters, OS availability, or runtime behavior.
- For Cherri, invoke the external binary without a shell, pass `--skip-sign`, use a timeout, validate the unsigned output, avoid clobbering existing intermediates, clean only files created by the invocation, and avoid echoing source diagnostics that may contain secrets.
- Cherri is not bundled, downloaded, or redistributed by ShortcutForge. Keep its separate license and platform-support status clear.
- Do not add control-flow serialization to the JSON compiler without a documented Apple format model and tests. Cherri is the code-first path for that today.

## Action catalog and iOS versions

- Ask users or Skill callers to select the iOS version installed on the target device before choosing actions. Current values: 17, 18, 26, 27.
- Query the selected release with `shortcutforge actions list --os VERSION`. Never infer availability from another iOS release.
- If evidence is unknown, state that and seek an export or reliable source from the exact target version. A version-filtered result remains evidence, not an on-device guarantee.
- Keep identifier observation, parameter evidence, version availability, and import/runtime verification as distinct claims.
- Preserve source URL, date/version, provenance, and license notices. Keep English and Japanese guides aligned.
- The Python public API uses `IOSVersion` and `ActionCatalog`; retain compatibility functions in `catalog.py` unless an explicitly documented breaking change is intended.

## Skill maintenance

- Keep `skills/shortcutforge/SKILL.md` focused on when and how a harness uses the actual CLI.
- Include supported commands, target-iOS selection, source-format choice (JSON vs Cherri), validation steps, unsigned-output handling, signer privacy disclosure, and exact limits.
- Never tell the harness that `validate` proves an action works or that an unsigned file can be imported.
- Avoid model/vendor-specific API assumptions. The caller's AI supplies reasoning; no model API key is required by ShortcutForge.
- Keep examples executable and consistent with current command syntax. Use separate docs for lengthy references.

## Documentation policy

- English and Japanese READMEs must describe the same capabilities and limits.
- Update the relevant docs, Skill, examples, and API references whenever a command or support claim changes.
- `docs/README.md` is the documentation index. Put system boundaries in `docs/architecture.md`, data flows in `docs/security.md`, and evidence definitions in the catalog source guide.
- Say explicitly when iPhone import/runtime or a particular iOS version has not been tested.
- Welcome catalog corrections and additions. A useful PR includes the exact action identifier, target iOS version/build and device or simulator, source/evidence, observed parameter keys, and whether the action was imported or run.

## Quality checks

From the repository root:

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m compileall -q src
git diff --check
```

Tests using mocks do not count as live Apple, Cherri-on-device, or remote signing validation. For code changes, add or update focused tests and run the relevant suite and checks. Report exactly which checks ran and which behaviors remain unverified.

## Repository hygiene and agent constraints

- Keep user-generated `.shortcut` files, secrets, credentials, personal data, and temporary compiler outputs out of commits.
- Inspect the final diff for stale claims, accidental generated files, secrets, unrelated edits, and English/Japanese drift.
- Use small, reviewable changes and preserve existing behavior outside the requested scope.
- Do not change repository visibility, publish releases, delete user data, or create external artifacts unless explicitly requested.
- Never describe incomplete or experimental behavior as supported. If a request cannot be completed, identify the concrete blocker and the best available alternative.
