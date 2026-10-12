# ShortcutForge

Python 3.11+ CLI and AI-harness Skill for building Apple Shortcuts from typed JSON. Python validates plans and emits binary plists; the calling harness interprets natural language. No GUI, daemon, or AI API is included.

## Install and use

```sh
python -m pip install .
shortcutforge actions list --os 27
shortcutforge actions list --os 27 --query calendar --format table
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
shortcutforge build examples/hello.json -o NotifyTime.shortcut
shortcutforge validate NotifyTime.shortcut
shortcutforge inspect NotifyTime.shortcut
```

Install the shared Skill at `skills/shortcutforge` in Codex or Claude Code; see its `SKILL.md` for harness-specific locations and the workflow.

Before using the action catalog, select the target iOS version. Choose `17`, `18`, `26`, or `27`; `--lang` selects English (`en`) or Japanese (`ja`). Markdown output can be saved directly with `--output`. Read the [English catalog guide](docs/action-catalog.en.md) or [Japanese catalog guide](docs/action-catalog.ja.md).

The same catalog is available as a typed Python API:

```python
from shortcutforge import ActionCatalog, IOSVersion

catalog = ActionCatalog.from_package()
actions = catalog.list_actions(IOSVersion.IOS_26, query="calendar")
status = catalog.get_availability("is.workflow.actions.notification", IOSVersion.IOS_26)
markdown = catalog.render_markdown(IOSVersion.IOS_26, language="ja", query="calendar")
```

## Signing and privacy

The private GitHub Actions workflow invokes Apple's `shortcuts sign --mode anyone` on macOS. Live testing confirmed GitHub-hosted macOS runners need an iCloud sign-in and fail without it. ShortcutForge places the base64 payload in a uniquely named repository secret, dispatches the workflow, then removes that secret; the runner masks its value in logs. Payloads must be under 60 KB encoded. Apple receives a copy for validation. Artifacts expire after one day. See `docs/signing-validation.md` for the live result and limitation.

## JSON plans and manual authoring

Plans accept three levels of detail: a readable catalog action ID and parameter names, Apple parameter keys for catalogued actions, or a raw Apple action identifier with its complete parameter dictionary. Raw values may be nested JSON objects and arrays when they match plist-compatible types.

Readable form:

```json
{"version":1,"name":"Notify current time","actions":[{"id":"current_date","as":"now"},{"id":"notify","params":{"text":{"ref":"now"}}}]}
```

Apple-key form (equivalent parameter spelling):

```json
{"version":1,"name":"Notify","actions":[{"id":"notify","params":{"WFNotificationActionBody":"Hello"}}]}
```

Raw action form (for actions not in the convenience catalog):

```json
{"version":1,"name":"Raw notification","actions":[{"identifier":"is.workflow.actions.notification","params":{"WFNotificationActionBody":"Hello","WFNotificationActionSound":false}}]}
```

Use `id` for a known catalog action and `identifier` for an explicit Apple action identifier. Raw actions receive basic JSON/plist validation; ShortcutForge cannot verify their iOS availability, required parameters, or runtime behavior. You can choose either style per action. Do not provide the same parameter twice using both spellings.

## Current limits

The discovery index contains 2,501 identifiers and provenance, while the build-time convenience schemas remain limited to current date, text, notification, speech, and URL. See [catalog coverage and sources](docs/action-catalog-sources.md). iOS 27 entries are simulator observations; iOS 17/18/26 availability is unknown because exact complete snapshots were not found. Binary plist validity does not prove Apple Shortcuts accepts or executes a file. Conditional/loop compilation and calendar actions are not implemented. No real iPhone import or runtime validation has been performed.

## Contributing catalog corrections

Pull requests correcting or adding action identifiers, iOS-version change notes, source links, or English/Japanese catalog text are welcome. Include the source and the exact iOS version/device or simulator used where available. Keep unverified compatibility clearly labeled as unknown.

## Development

```sh
python -m unittest discover -s tests -v
```

MIT licensed.
