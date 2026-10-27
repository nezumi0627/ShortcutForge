# iOS action compatibility and verification

## Current result

| Evidence level | iOS 17 | iOS 18 | iOS 26 | iOS 27 |
| --- | --- | --- | --- | --- |
| Exact complete identifier snapshot | Not available | Not available | Not available | 1,206 identifiers observed in iOS 27.0 Simulator ToolKit v78 |
| Generated schemas in ShortcutForge | No per-version schema snapshot | No per-version schema snapshot | No per-version schema snapshot | 212 schemas selected from a macOS-oriented definition set, cross-checked against iOS 27 identifiers and parameter-key observations |
| Import/run on a physical iPhone in this project | Not tested | Not tested | Not tested | Not tested |

**Do not treat a generated iOS 27 schema as compatible with iOS 17, 18, or 26.** Its exact identifier is present in an iOS 27 Simulator index, while its parameter definitions come from `scpl-macos-updated` v2.3.1. The source does not provide a matching iOS 17/18/26 parameter snapshot. These generated schemas are currently experimental across all iOS releases, including iOS 27 physical devices.

## Version-specific facts from public release references

These release notes establish feature names and platform availability, but not a complete internal-ID or parameter catalog:

- **iOS 17:** Apple's notes list `Delete Alarms`, `Edit Sleep Alarm`, timer and stopwatch controls, `Open Camera`, `Open Collection`, `Show Passwords`, `End Workout`, `Scan Document`, hotspot/cellular controls, and `Transcribe Audio`. iOS 17.4 adds `Get Orientation` and `Get Activity`. A community comparison notes the File/Folder change and a `Recognize Music` rename. These names do not establish plist schemas for the generated actions.
- **iOS 18:** Apple's notes list `Create Entry`, `Create Audio Entry`, `Search Entries`, Magnifier actions, `Create Board`/`Open Board`, `Set Music Focus Filter`, and `Open Card` in 18.0; `Get Current App`, Fitness, Freeform, Stocks, and app-specific actions in later point releases; and Notes actions in 18.5. These feature notes do not establish internal identifiers or parameter serialization for our generated catalog.
- **iOS 26:** Apple documents `Create Image`, `Find Message`, `Find Conversation`, `Get App & Website Data`, `Get Upcoming Sports Events`, Photos and Reminders actions, `Use Model`, Writing Tools actions, and `Set Battery Charge Limit` in 26.4. Partial community comparisons cover changes through 26.4; their authors warn that simulator databases omit some built-in apps and block actions.
- **iOS 27:** the bundled simulator catalog provides identifier and partial parameter-key/type evidence. The 212 generated schemas are cross-referenced against observed identifiers, and every generated parameter key is present in the iOS 27 parameter snapshot where one exists. Ten candidate schemas were excluded because their parameter keys conflicted with that snapshot. Parameter values and serialization have not been confirmed by importing all of them on iPhone.

Sources: [Apple's iOS 17 Shortcuts notes](https://support.apple.com/en-au/111098), [Apple's iOS 18 Shortcuts notes](https://support.apple.com/en-au/121131), [Apple's iOS 26 Shortcuts notes](https://support.apple.com/en-gb/125148), [community iOS 17 action comparison](https://talk.automators.fm/t/ios-16-17-new-and-updated-actions-and-backward-incompatibility/16523), [iOS 18 to 26.1 comparison](https://talk.automators.fm/t/ios-18-26-1-new-and-updated-actions/19029), [26.2 to 26.4 comparison](https://talk.automators.fm/t/os-26-2-26-4-new-and-updated-actions/19117), and [26 to 27 comparison](https://talk.automators.fm/t/os-26-27-new-and-updated-actions/19177).

## Additional independent test evidence

The public [`shortcut-lib`](https://github.com/findlaywebb/shortcut-lib) project reports an end-to-end iPhone test on **iOS 26.4.2** for one workflow using Clipboard, Use Model, date/text, Base64, URL request, and notification actions. This supports that those action families can participate in at least one real iOS 26.4.2 shortcut. It does not test ShortcutForge's generated PLISTs, validate every parameter variant, or cover the other 212 schemas. The project is GPL-3.0; ShortcutForge references its published test report only and does not copy its code or sample data.

The public [`shortcutkit`](https://github.com/frontboat/shortcutkit) project documents catalog extraction from **macOS 27.2**. Its larger extracted catalog is useful for macOS schema research, but it is not evidence for iOS 17, 18, or 26 compatibility.

## What was checked locally

All 212 generated schemas are emitted together and parsed as a binary plist by the local unit tests. This checks ShortcutForge's own data and serializer, not Apple runtime compatibility. A signed smoke shortcut was also built with one generated action (`Get Battery Level`) followed by `Show Result`; it displays the current battery percentage and makes no changes to device data.

This checkout is running on Windows. It has no `xcrun`, Xcode/iOS Simulator, macOS Shortcuts app, or connected iPhone. Therefore the project cannot perform an actual import/run check against iOS 17, 18, 26, or 27 from this machine.

## Device verification needed

For a reproducible compatibility claim, test the signed smoke shortcut on an iPhone running each target iOS release, then use individually reviewed samples for additional action schemas. The smoke source is [`ios-compatibility-smoke.json`](../examples/ios-compatibility-smoke.json). For each device:

1. Record the exact iOS version/build and device model.
2. Import the signed `.shortcut` in the Shortcuts app and note any missing/unknown actions.
3. Run it and confirm the battery percentage appears. This confirms only the smoke workflow on that device.
4. For each additional action under test, use a separate safe shortcut and record success/failure; do not run destructive actions as smoke tests.
5. Export the resulting shortcut or share sanitized screenshots/logs, removing personal data.

Keep identifier discovery, parameter-schema evidence, successful import, and successful runtime execution as separate evidence levels. A result on one iOS version must not be copied to another version without evidence.
