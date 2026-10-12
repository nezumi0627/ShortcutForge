# ShortcutForge

Python 3.11+ CLI and AI-harness Skill for building Apple Shortcuts from typed JSON. Python validates plans and emits binary plists; the calling harness interprets natural language. No GUI, daemon, or AI API is included.

## Install and use

```sh
python -m pip install .
shortcutforge actions list
shortcutforge build examples/hello.json -o Hello.shortcut
shortcutforge validate Hello.shortcut
shortcutforge inspect Hello.shortcut
```

Install the shared Skill at `skills/shortcutforge` in Codex or Claude Code; see its `SKILL.md` for harness-specific locations and the workflow.

## Signing and privacy

The private GitHub Actions workflow invokes Apple's `shortcuts sign --mode anyone` on macOS. Live testing confirmed GitHub-hosted macOS runners need an iCloud sign-in and fail without it. ShortcutForge places the base64 payload in a uniquely named repository secret, dispatches the workflow, then removes that secret; the runner masks its value in logs. Payloads must be under 60 KB encoded. Apple receives a copy for validation. Artifacts expire after one day. See `docs/signing-validation.md` for the live result and limitation.

## Current limits

The action catalog is intentionally small. Unknown actions fail closed. Binary plist validity does not prove Apple Shortcuts accepts or executes a file. Conditional/loop compilation, rich variable interpolation, and broad calendar/action coverage are not implemented. No real iPhone import or iOS 27 validation has been performed.

## Development

```sh
python -m unittest discover -s tests -v
```

MIT licensed.
