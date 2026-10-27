# ShortcutForge

**Create Apple Shortcuts from typed JSON or [Cherri](https://github.com/electrikmilk/cherri) source.** ShortcutForge is a Python command-line tool and reusable Skill for Codex and Claude Code. An AI harness can interpret a request and draft a workflow; people can also author JSON or Cherri directly. ShortcutForge validates and compiles locally, without an LLM API.

[日本語](README.ja.md) · [Documentation](docs/README.md) · [Contributing](docs/contributing.md) · [MIT License](LICENSE)

> **Signing and import:** `build` creates an unsigned `.shortcut`. Sign it before importing the file into Apple Shortcuts on iPhone or iPad. Windows currently supports Shortcuty only; that option uploads the complete shortcut to Shortcuty's service. Supported non-Windows hosts can use HubSign or Apple's macOS signer. GitHub Actions are not used to sign shortcuts. Read [signing and privacy](docs/signing-validation.md) before sending a workflow to a remote signer.

## What ShortcutForge does

- Compiles versioned JSON plans using the built-in Python compiler.
- Delegates `.cherri` source to a separately installed Cherri compiler, with Cherri signing disabled.
- Validates basic workflow plist structure and inspects existing workflows without executing them.
- Searches a version-scoped action discovery catalog for iOS 17, 18, 26, and 27, with English and Japanese Markdown output.
- Provides a harness-neutral Skill. The AI interprets intent; ShortcutForge makes no model or network calls during build, validate, or inspect.

The JSON compiler currently exposes 301 named schemas: 19 hand-curated actions plus 282 sourced schemas. The generated set includes Apple and app-provided actions whose identifiers and parameter keys were observed in iOS 27 Simulator data. App-provided actions may require their app. The larger 2,501-identifier catalog is a research index; observation does not guarantee import or runtime support on a device.

## Install

Requires Python 3.11 or newer.

```sh
python -m pip install .
```

Use `python -m shortcutforge` if the installed `shortcutforge` command is not on `PATH`.

Cherri builds are optional and require the separate Cherri executable on `PATH`. See [Cherri integration](docs/cherri-integration.md) for installation and Windows limitations.

## Build a JSON shortcut

Create `plan.json`:

```json
{
  "version": 1,
  "name": "Notify current time",
  "actions": [
    {"id": "current_date", "as": "now"},
    {"id": "notify", "params": {"text": {"ref": "now"}}}
  ]
}
```

Compile, inspect, then sign before importing:

```sh
shortcutforge build plan.json -o NotifyCurrentTime.shortcut
shortcutforge validate NotifyCurrentTime.shortcut
shortcutforge inspect NotifyCurrentTime.shortcut
shortcutforge sign NotifyCurrentTime.shortcut
```

The compiler includes named actions for text and input, notifications and speech, URLs and web requests, clipboard, location and device details, calendar events and reminders, Photos, battery level, and delay, plus over 200 sourced actions with supported parameter formats. See the [full list, sources, and limits](docs/named-actions.md). Raw Apple action identifiers and parameter dictionaries can also be supplied, but ShortcutForge only performs structural checks on raw actions. See the [JSON plan reference](docs/json-plan-format.md).

## Build Cherri source

Cherri is a separate language and compiler suited to code-first workflows, including control flow and functions. Install Cherri, then:

```sh
shortcutforge build examples/cherri-control-flow.cherri -o CherriExample.shortcut
shortcutforge validate CherriExample.shortcut
shortcutforge inspect CherriExample.shortcut
```

ShortcutForge invokes Cherri with `--skip-sign`, validates its unsigned plist, and writes the requested output. Signing is a separate explicit step. The included example demonstrates an If and Repeat. A Windows smoke test succeeded with Cherri built from upstream source; upstream's platform guidance still cautions that Windows is not reliably supported. See the [integration guide](docs/cherri-integration.md).

## Choose actions for the target iOS version

Select the iOS version installed on the target device before choosing actions. The catalog can help find identifiers and evidence, but it is incomplete and does not guarantee import or runtime behavior.

```sh
shortcutforge actions list --os 27 --query notification
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
shortcutforge actions list --os 18 --format json
```

Read the [English catalog guide](docs/action-catalog.en.md), [Japanese catalog guide](docs/action-catalog.ja.md), and [iOS 26/27 research and coverage](docs/ios26-27-catalog-research.md). iOS 27 includes 1,206 simulator-observed identifiers and detailed parameter metadata where available. iOS 26 includes individually sourced version changes, but no complete exact-ID or parameter snapshot is publicly available. Corrections and additions are welcome; please include version-specific evidence in a [pull request](docs/contributing.md).

Python callers can query the same versioned catalog:

```python
from shortcutforge import ActionCatalog, IOSVersion

catalog = ActionCatalog.from_package()
actions = catalog.list_actions(IOSVersion.IOS_26, query="calendar")
availability = catalog.get_availability(
    "is.workflow.actions.notification", IOSVersion.IOS_26
)
markdown = catalog.render_markdown(IOSVersion.IOS_26, language="ja")
```

## AI harness Skill

The [ShortcutForge Skill](skills/shortcutforge/SKILL.md) contains the workflow for Codex and Claude Code. Install ShortcutForge with `python -m pip install .`, then copy or link `skills/shortcutforge` into the harness's skills directory. The Skill uses the harness's own reasoning; it requires no model API key. It checks the target iOS version, builds and inspects a workflow, then treats signing as a separate data-sharing decision.

## Commands

| Command | Purpose |
| --- | --- |
| `shortcutforge build PLAN.json -o FILE` | Validate a JSON plan and compile a binary plist. |
| `shortcutforge build SOURCE.cherri -o FILE` | Compile with the separately installed Cherri compiler, unsigned. |
| `shortcutforge validate FILE` | Check plist structure; Apple action semantics are not verified. |
| `shortcutforge inspect FILE` | Show workflow metadata and action identifiers without executing it. |
| `shortcutforge actions list --os VERSION` | Search the action discovery catalog for one iOS version. |
| `shortcutforge sign FILE` | Sign with Shortcuty by default; only Shortcuty is enabled on Windows. |

Run `shortcutforge COMMAND --help` for options. On supported non-Windows hosts, signing can also select HubSign or Apple's local macOS command. See [signing setup](docs/signing-validation.md).

## Limits and verification status

- The generated compiler schemas are a filtered subset of the discovery catalog; many identifiers still have unsupported parameter formats and cannot be built as named actions.
- A valid plist does not prove that Shortcuts recognizes, imports, or runs a workflow.
- Cherri is optional and maintained separately. ShortcutForge has smoke-tested one If/Repeat example on Windows; this does not establish support for every Cherri feature or release.
- Catalog evidence for iOS 27 is simulator-based. Coverage for iOS 17, 18, and 26 is partial or unknown.
- No physical iPhone import or runtime test has been completed. iOS 27 import remains unverified.
- See the [version-by-version compatibility evidence and verification limits](docs/action-compatibility.md).
- Build outputs are unsigned. Shortcuty and HubSign receive the shortcut remotely; Apple's macOS signer also sends a copy to Apple for validation. Windows methods other than Shortcuty remain research-only.

## Development

```sh
python -m unittest discover -s tests -v
python -m compileall -q src
```

See [architecture](docs/architecture.md), [security](docs/security.md), [contribution guidance](docs/contributing.md), and [AGENTS.md](AGENTS.md). This public repository is also a GitHub template; review [template setup](docs/template-and-release.md) before creating a derived project.
