# ShortcutForge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a private template repository containing a cross-platform Python CLI and harness-neutral Skill that compiles typed shortcut plans and orchestrates Apple signing through GitHub Actions.

**Architecture:** Keep deterministic JSON validation, plist serialization, inspection, and Actions API interaction in Python 3.11+ with standard library only. The Skill directs Codex/Claude Code to interpret the request and call the CLI; macOS Actions performs Apple's signing command.

**Tech Stack:** Python 3.11+, `plistlib`, `argparse`, GitHub CLI/API, GitHub Actions macOS runner, unittest.

**Spec:** User-provided ShortcutForge development instructions; initial repository policy in `AGENTS.md`.

## Global Constraints

- Python 3.11+, standard library preferred, binary plist output, Windows/Linux CLI support.
- No GUI, web app, daemon, or independent AI API.
- Private GitHub template, MIT license, default branch `main`.
- Unknown actions and invalid IR fail closed.
- Never log or commit user shortcuts, credentials, or generated signed artifacts.
- Apple device/iOS 27 compatibility must be identified as unverified unless actually tested.

## Review Focus

- Unknown or malformed action data must fail before output: validator rejection tests.
- Variable references and control-flow nesting must not allow dangling references: IR tests.
- User payloads must not reach git history or Actions logs: workflow review and payload-free test.
- Artifact polling must stop at a bounded timeout and report failures safely: signing client tests.
- Plist inspection must not execute shortcut actions: parser tests with unknown action fixture.

## File Map

- `src/shortcutforge/ir.py`: typed IR decoding and schemas.
- `actions/catalog.json`: supported action metadata.
- `src/shortcutforge/validator.py`: structural and reference validation.
- `src/shortcutforge/compiler.py`: IR to binary plist.
- `src/shortcutforge/parser.py`: safe plist inspection.
- `src/shortcutforge/signing.py`: GitHub CLI workflow dispatch/poll/artifact client.
- `src/shortcutforge/cli.py`, `__main__.py`: CLI commands.
- `.github/workflows/sign.yml`: private, concurrency-limited macOS signing.
- `.github/workflows/test.yml`: standard-library tests.
- `skills/shortcutforge/SKILL.md`: Codex/Claude harness-neutral instructions.
- `tests/`, `examples/`, `README.md`, `pyproject.toml`, `LICENSE`.

### Task 1: Signing feasibility probe

**Files:** `.github/workflows/sign.yml`, `tests/fixtures/unsigned-smoke.shortcut` (synthetic only), `docs/signing-validation.md`

- [ ] Add a manual workflow that signs only a synthetic payload with `/usr/bin/shortcuts sign --mode anyone` on macOS; no payload logging, least permissions, concurrency group, short artifact retention.
- [ ] Dispatch it and inspect run result, logs, and artifact availability.
- [ ] Record whether Apple account setup is required and whether a hosted runner can complete signing; if blocked, document observed error and viable supported path.

### Task 2: Python package and typed IR

- [ ] Add package metadata, MIT license, ignores, CLI entrypoint.
- [ ] Define versioned JSON schema in typed dataclasses; reject unknown fields/types.
- [ ] Add catalog entries only for actions whose plist representation is evidenced; mark unsupported actions explicitly.

### Task 3: Validation, compilation, and inspection

- [ ] Validate actions, parameters, control flow, variable definitions/references.
- [ ] Compile supported IR to binary plist using `plistlib`.
- [ ] Inspect existing plists read-only and identify unknown actions without execution.
- [ ] Cover required examples/tests; do not assert device compatibility without a device.

### Task 4: Actions signing client

- [ ] Implement workflow dispatch, bounded polling, sanitized logs/errors, artifact download, retry, temporary cleanup, and run-level concurrency semantics via GitHub CLI/API.
- [ ] Keep artifact private and short-lived; use an ephemeral branchless workflow input mechanism.
- [ ] Add mocked client tests and document the live workflow result from Task 1.

### Task 5: Skill and docs

- [ ] Write portable `SKILL.md` with frontmatter, task flow, CLI examples, limitations, installation paths for Codex and Claude Code.
- [ ] Document build/validate/inspect/sign, action support, privacy, and iOS 27 status.
- [ ] Generate a safe sample shortcut, run all requested automated checks, review git diff for sensitive data, commit and push.
- [ ] Verify private/template/main settings after push.
