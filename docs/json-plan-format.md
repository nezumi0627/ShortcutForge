# JSON plan format

ShortcutForge accepts a JSON object with a versioned, ordered list of actions. Plans are intended to be easy to create and review by hand.

## Top-level fields

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `version` | integer | yes | Currently `1`. |
| `name` | non-empty string | yes | Shortcut display name in the workflow plist. |
| `actions` | array | yes | Actions in execution order. |

Unknown top-level fields are rejected. Each action is an object containing exactly one of `id` or `identifier`, optional `params` (an object; defaults to `{}`), and optional `as` (a non-empty output name when used).

## Named actions

Use a readable ID from the small compiler schema. Parameter aliases are converted to Apple plist keys during compilation.

```json
{
  "version": 1,
  "name": "Say hello",
  "actions": [
    {"id": "text", "params": {"text": "Hello from ShortcutForge"}, "as": "greeting"},
    {"id": "speak", "params": {"text": {"ref": "greeting"}}}
  ]
}
```

Current named IDs and aliases:

| ID | Accepted parameter | Output |
| --- | --- | --- |
| `current_date` | `mode` or `WFDateActionMode` (defaults to `Current Date`) | yes |
| `text` | `text` or `WFTextActionText` | yes |
| `notify` | `text` or `WFNotificationActionBody` | no |
| `speak` | `text` or `WFSpeakTextText` | no |
| `open_url` | `url` or `WFURLActionURL` | no |

Parameters can use catalog aliases or Apple plist parameter keys. Do not provide one parameter twice under both spellings. Only known named actions get schema and output-reference validation.

## Output references

Set `as` on an action that produces output, then refer to it in a later named action using the exact object `{"ref":"output_name"}`. References must point to an earlier output-producing action. Duplicate names, forward references, and references to actions without output are rejected.

The version 1 schema is a flat, ordered action list; it has no typed fields for conditions, loops, or nested blocks. A hand-authored plan can encode Apple control flow as raw marker actions with matching grouping IDs (see the example below), but the validator does not check their structure or semantics. The marker pattern is documented in community references such as [Shortcuts Playground](https://github.com/viticci/shortcuts-playground-plugin/blob/main/codex/skills/shortcuts-playground/SKILL.md) and [clean-shortcuts control flow](https://github.com/damionrashford/clean-shortcuts/blob/main/Documentation/CONTROL-FLOW.md); neither is an Apple compatibility guarantee. Calendar access is not implemented as a named action.

## Raw Apple actions

Use `identifier` for an exact Apple action identifier not present in the named convenience schema:

```json
{
  "version": 1,
  "name": "Raw notification",
  "actions": [
    {
      "identifier": "is.workflow.actions.notification",
      "params": {
        "WFNotificationActionBody": "Hello",
        "WFNotificationActionSound": false
      }
    }
  ]
}
```

Raw parameters must be JSON values compatible with plist serialization (objects with string keys, arrays, strings, booleans, integers, and finite numbers). `null` is not supported. ShortcutForge does not know if a raw action exists on the selected iOS release, whether its parameters are complete, or whether Apple will import or execute it. Control flow can be represented as a flat sequence of raw actions sharing a `GroupingIdentifier` and using `WFControlFlowMode` markers; ShortcutForge does not validate that the groups are balanced or semantically correct. See the [Battery Decision Lab example](../examples/battery-decision-lab.json) and inspect an actual shortcut from the selected iOS version before relying on a raw shape.

## CLI workflow

```sh
shortcutforge build plan.json -o Result.shortcut
shortcutforge validate Result.shortcut
shortcutforge inspect Result.shortcut
```

`validate` checks plist/workflow structure; it does not verify Apple action semantics. `inspect` reads the file without running it. Keep personal data and secrets out of example plans and shared PRs. See [security](security.md).

`build` writes an unsigned binary plist. A signed `.shortcut` is required before importing the file into Shortcuts on iPhone/iPad. See [signing validation and available paths](signing-validation.md); a successful `validate` result does not prove that a file is signed or importable.
