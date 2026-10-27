# Named JSON actions

ShortcutForge's JSON compiler combines hand-curated schemas with a sourced generated subset. The schemas make common plans easier to read and catch input mistakes. They are not a complete Apple Shortcuts API and do not prove that an action exists or runs on a particular device.

## Sourced generated actions

In addition to the hand-curated entries below, the compiler loads **212 generated action schemas** from [`scpl_ios27_actions.json`](../src/shortcutforge/data/scpl_ios27_actions.json). Each generated ID is derived from the action's published English name (lowercase snake case); parameter names are the exact plist keys. The data is filtered to identifiers independently observed in the iOS 27 Simulator catalog, parameter keys cross-checked against its parameter snapshot, and parameter classes the current compiler can represent as direct plist values. Ten mismatched candidates are retained in the JSON file's exclusion list with their conflicting keys.

Version compatibility and the limits of simulator and device verification are documented in [action compatibility](action-compatibility.md).

The generated definitions originate from [`scpl-macos-updated` v2.3.1](https://github.com/cavingraves/scpl-macos-updated), a community-maintained macOS-oriented snapshot. Its MIT license is included at [`SCPL-MIT-LICENSE`](../src/shortcutforge/data/SCPL-MIT-LICENSE). The action identifiers are cross-checked against [Shortcut Playground ToolKit v78](https://github.com/viticci/shortcuts-playground-plugin), whose iOS 27 Simulator evidence supports presence of identifiers only; it does not establish parameter behavior. iOS 17, 18, and 26 availability and real-device import/run behavior remain unverified for these generated schemas.

Parameters on generated actions are optional unless an action has a source default. This is deliberate: upstream data does not consistently identify required inputs. Generated action parameters use exact Apple plist keys, and only documented string `Items` are enforced as choices. Actions without known output metadata cannot be used as named outputs. For unsupported parameter classes, use a real exported shortcut as a raw action rather than guessing its serialization.

Search the discovery catalog by name or identifier, then use a generated ID and exact plist keys in JSON. The action discovery command is an index and may include entries that have no generated build schema; refer to `scpl_ios27_actions.json` for the exact supported IDs.

## Supported actions

| ID | Apple identifier | Parameter aliases → plist keys | Output |
| --- | --- | --- | --- |
| `current_date` | `is.workflow.actions.date` | `mode` → `WFDateActionMode` (default `Current Date`) | Yes |
| `text` | `is.workflow.actions.gettext` | `text` → `WFTextActionText` (required) | Yes |
| `notify` | `is.workflow.actions.notification` | `text` → `WFNotificationActionBody` (required) | No |
| `speak` | `is.workflow.actions.speaktext` | `text` → `WFSpeakTextText` (required) | No |
| `open_url` | `is.workflow.actions.openurl` | `url` → `WFURLActionURL` (required) | No |
| `ask_for_input` | `is.workflow.actions.ask` | `prompt` → `WFAskActionPrompt` (required); `input_type` → `WFInputType` (default `Text`); `default_answer` → `WFAskActionDefaultAnswer`; `default_date` → `WFAskActionDefaultAnswerDate`; `granularity` → `WFAskActionDateGranularity` | Yes |
| `get_clipboard` | `is.workflow.actions.getclipboard` | — | Yes |
| `set_clipboard` | `is.workflow.actions.setclipboard` | `input` → `WFInput` (required output reference) | No |
| `get_current_location` | `is.workflow.actions.getcurrentlocation` | — | Yes |
| `get_device_details` | `is.workflow.actions.getdevicedetails` | `detail` → `WFDeviceDetail` (default `Device Name`) | Yes |
| `get_upcoming_events` | `is.workflow.actions.getupcomingevents` | `calendar` → `WFGetUpcomingItemCalendar`; `count` → `WFGetUpcomingItemCount` (default `1`); `day` → `WFDateSpecifier` (default `Any Day`); `specified_day` → `WFSpecifiedDate` | Yes |
| `get_upcoming_reminders` | `is.workflow.actions.getupcomingreminders` | `list` → `WFGetUpcomingItemCalendar`; `count` → `WFGetUpcomingItemCount` (default `1`) | Yes |
| `get_current_ip_address` | `is.workflow.actions.getipaddress` | `address` → `WFIPAddressSourceOption` (default `External`); `type` → `WFIPAddressTypeOption` (default `IPv4`) | Yes |
| `get_latest_photos` | `is.workflow.actions.getlastphoto` | `count` → `WFGetLatestPhotoCount` (default `1`); `include_screenshots` → `WFGetLatestPhotosActionIncludeScreenshots` (default `true`) | Yes |
| `get_contents_of_url` | `is.workflow.actions.downloadurl` | `url` → `WFURL` (required; default HTTP GET) | Yes |
| `show_result` | `is.workflow.actions.showresult` | `text` → `Text` (required) | No |
| `save_to_photos` | `is.workflow.actions.savetocameraroll` | `input` → `WFInput` (required output reference) | Yes |
| `get_battery_level` | `is.workflow.actions.getbatterylevel` | — | Yes |
| `delay` | `is.workflow.actions.delay` | `seconds` → `WFDelayTime` (default `1`, number) | No |

Additional validation checks enum choices for `ask_for_input.input_type`, `get_upcoming_events.day`, and `get_current_ip_address`; numeric/integer/boolean shapes for the parameters that declare them; and the conditional date fields for input/calendar actions. These checks validate the JSON plan only, not Apple's runtime behavior.

Readable aliases and their plist keys are defined in [`actions.py`](../src/shortcutforge/actions.py). For reference parameters, ShortcutForge emits either a `WFTextTokenString` or `WFTextTokenAttachment` according to the receiving action's schema. The token shapes follow exported workflow examples and the public [Shortcuts plist format notes](https://github.com/viticci/shortcuts-playground-plugin/blob/main/codex/skills/shortcuts-playground/PLIST_FORMAT.md).

## Example: calendar events

```json
{
  "version": 1,
  "name": "Show upcoming events",
  "actions": [
    {
      "id": "get_upcoming_events",
      "params": {"calendar": "All", "count": 5, "day": "Today"},
      "as": "events"
    },
    {"id": "show_result", "params": {"text": {"ref": "events"}}}
  ]
}
```

## Evidence and compatibility

- Parameter keys, defaults, allowed values, and outputs were cross-checked against the public [ScPL action reference](https://docs.scpl.dev/) and the repository's [iOS 27 Simulator action metadata](https://github.com/viticci/shortcuts-playground-plugin). The two sources have different ages and coverage; see [catalog source notes](action-catalog-sources.md).
- Parameter and output details were cross-checked against ScPL's [Ask for Input](https://docs.scpl.dev/actions/askforinput), [Get Device Details](https://docs.scpl.dev/actions/getdevicedetails), [Get Upcoming Events](https://docs.scpl.dev/actions/getupcomingevents), [Get Upcoming Reminders](https://docs.scpl.dev/actions/getupcomingreminders), [Get Contents of URL](https://docs.scpl.dev/actions/getcontentsofurl), [Get Clipboard](https://docs.scpl.dev/actions/getclipboard), [Copy to Clipboard](https://docs.scpl.dev/actions/copytoclipboard), [Save to Photo Album](https://docs.scpl.dev/actions/savetophotoalbum), [Get Current IP Address](https://docs.scpl.dev/actions/getcurrentipaddress), [Get Latest Photos](https://docs.scpl.dev/actions/getlatestphotos), [Get Battery Level](https://docs.scpl.dev/actions/getbatterylevel), and [Wait](https://docs.scpl.dev/actions/wait).
- `show_result` uses the `Text` parameter key and displays the supplied text as described by ScPL's [Show Result reference](https://docs.scpl.dev/actions/showresult).
- Current-location output and its location permission/background limitations are described in [Get Current Location](https://docs.scpl.dev/actions/getcurrentlocation).
- The catalog reports exact identifier observations for iOS 27 Simulator, but that does not establish the exact parameter schema on iOS 27 or availability on iOS 17, 18, or 26. The named schemas have not been tested by importing and running each generated action on physical iPhones.
- `validate` confirms only the plan and plist structure. It cannot confirm permission prompts, action availability, parameter semantics, network responses, or Photos behavior on a device.
- The JSON plan still has no structured If/Repeat builder. Use Cherri for code-first control flow, or raw identifiers only when you have a matching action export and accept structural-only validation.

When adding another named action, record its exact identifier, parameter keys, required/default values, output/reference shape, evidence URLs, and target OS/platform. Add focused input and plist-shape tests in the same change, then update this page and the JSON plan reference.
