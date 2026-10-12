# ShortcutForge Agent Instructions

## Purpose
Build a lightweight Python 3.11+ CLI and portable AI-harness Skill that compiles typed JSON shortcut plans into Apple Shortcuts binary plists, validates and inspects them, and optionally obtains an Apple-signed artifact through GitHub Actions. The user-facing goal is generating importable `.shortcut` files from natural language without a Mac.

## Architecture
- Prefer the Python standard library and explicit typed data structures.
- Keep parsing, validation, plist compilation, action metadata, CLI, and GitHub signing client separate only where their responsibilities require it.
- No GUI, web app, daemon, LLM API, or unrelated abstractions.
- Treat the JSON intermediate representation as untrusted input; validate before compilation.

## Coding conventions
- Support Python 3.11+; use type hints, clear errors, pathlib, and small functions.
- Keep dependencies minimal; document any non-standard dependency and why it is needed.
- Never silently emit partially valid shortcuts or claim unsupported actions work.
- Keep generated/private user data out of logs, fixtures, and commits.

## Directory structure
- `src/shortcutforge/`: CLI, IR, compiler, parser, validator, actions, and signing client.
- `skills/shortcutforge/`: portable `SKILL.md`, references, and helper scripts for Codex/Claude Code.
- `.github/workflows/`: isolated signing and test workflows.
- `examples/`, `tests/`: safe examples and automated tests.

## Shortcut generation specification
- Input is versioned JSON with shortcut metadata and an ordered list of typed actions.
- Output is an Apple binary plist `.shortcut` file.
- Support explicit action parameters, output references, variables, conditionals, and repeat blocks only where the compiler/catalog defines a valid mapping.
- Inspect existing plist files without executing them; report unknown actions and malformed structures.
- Maintain an explicit action catalog. Unknown or unsupported actions fail validation.

## Action addition rules
- Add an action only with a documented identifier, parameter schema, input/output behavior, and a fixture or test.
- Do not infer undocumented Apple serialization details and present them as supported.
- Preserve source references for catalog research where practical.

## Tests and quality
- Run the requested unit tests and CLI checks; cover valid and invalid IR and binary plist round-trips.
- Include safe fixtures for notification, speech, URL, calendar, conditionals, loops, and variable references.
- Signing integration tests must not expose user payloads or secrets and must distinguish mocked tests from live macOS validation.
- State clearly when Apple-device execution or iOS 27 import has not been verified.

## GitHub Actions signing
- Signing runs only on a macOS runner using Apple's `/usr/bin/shortcuts sign --mode anyone`.
- Use workflow dispatch with a short-lived private artifact, no checkout of user payloads into git, no payload or secret logging, restrictive permissions, concurrency control, bounded timeout, and cleanup.
- Poll the workflow and retrieve its artifact with GitHub CLI/API; surface sanitized failure details.
- Verify on a real GitHub-hosted macOS runner whether `anyone` signing works without Apple account setup. Never claim the path works until verified.
- Keep the repository private and enable template mode only after the initial instructions commit is pushed.

## Security
- Never commit credentials, signed shortcuts, generated personal payloads, or live user data.
- Avoid shell interpolation of user-controlled values; use argument arrays and private temporary directories.
- Redact tokens and payload data from diagnostics. Treat workflow artifacts as sensitive and short-lived.
- Do not request or store Apple ID credentials unless a verified platform requirement makes them necessary and the user has explicitly approved the design.
- Template descendants must not inherit secrets, credentials, or private workflow run artifacts.

## Skill development and updates
- Keep `SKILL.md` harness-neutral, with valid frontmatter, direct CLI instructions, examples, and links to concise references.
- The calling model performs intent interpretation; the Python package performs deterministic compilation, validation, inspection, and signing orchestration.
- Update examples, tests, and docs whenever the IR or CLI changes.

## Agent constraints
- Follow the repository's instructions and the user's stated scope.
- Never overwrite an existing GitHub repository or existing user files.
- Do not claim full Apple compatibility from plist serialization alone.
- Report blockers, limitations, exact verification performed, and deliverable paths plainly.
