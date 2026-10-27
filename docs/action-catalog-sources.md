# Action catalog coverage and sources

## What the catalog means

The bundled catalog currently indexes **2,501 unique identifiers**. Of these, **1,206** were observed in the iOS 27.0 Simulator ToolKit v78 snapshot, and **1,146** identifiers have a sourced display name, and **1,072** records have iOS 27 parameter metadata covering **3,432** parameters. Relevant enum metadata covers **815** types and **4,676** cases. The snapshot also records parameter ordering, flags, tool types, and platform scope. The ToolKit v63 list contributes 1,794 identifiers, but declares no OS or platform. A separate unversioned public catalog contributes 415 references.

An observed identifier means only that the source snapshot contained that identifier. It does not prove a valid parameter schema, support on a physical iPhone, successful import, or working runtime behavior. `actions list` is a discovery index; only the hand-curated schemas and 282 sourced generated schemas described in [action compatibility](action-compatibility.md) are compiled through named IDs. Use a raw action definition only when its parameters are sourced from an actual compatible shortcut or reliable device export.

Independent reports of on-device testing are listed in [action compatibility](action-compatibility.md) with their exact scope; they do not transfer runtime evidence to ShortcutForge's compiler automatically.

## Per-version interpretation

- **iOS 27:** exact simulator identifier evidence is available for 1,206 IDs. This is not a physical-device compatibility test. Parameter metadata is retained when its source specifically lists the iOS 27 Simulator, including names, Python type names, order, flags, platform scope, and enum choices where catalogued.
- **iOS 17, iOS 18, and iOS 26:** no exact complete public snapshots were found. `--os` returns discovery candidates, and their `availability` remains `unknown`. ToolKit v63 is dated 2026-02-09 but does not identify its source OS; it is not treated as an iOS 26 catalog. The localized Markdown includes Apple-published named changes for iOS 17.4, iOS 18.0–18.5, and individually listed iOS 26.0 additions, plus partial community comparisons for 17, 26.1, and 26.4. Those names do not supply exact identifiers or parameter schemas.

Apple does not publish a complete official action ID and parameter schema catalog. Public sources include simulator/runtime snapshots, harvested identifiers, and unversioned references. Version claims therefore remain scoped to the evidence available for each record.

## Sources and licenses

- [Shortcuts Playground Plugin](https://github.com/viticci/shortcuts-playground-plugin): MIT; ToolKit v78 iOS 27 Simulator lists/parameter keys (snapshot dated 2026-06-13) and ToolKit v63 identifier baseline (2026-02-09). See the bundled `src/shortcutforge/data/viticci-LICENSE`.
- Apple Support release notes: [iOS 26 updates through 26.7.1](https://support.apple.com/en-ie/123075), [iOS/iPadOS/macOS/watchOS/visionOS 27 updates through 27.2](https://support.apple.com/en-us/149045), [iOS 17](https://support.apple.com/en-au/111098), [iOS 18](https://support.apple.com/en-au/121131), and [iOS 26](https://support.apple.com/en-gb/125148). These report user-facing action names and supported platforms, not internal action schemas.
- [mcp-server-ios-shortcuts](https://github.com/truth0530/mcp-server-ios-shortcuts): MIT; 415-entry unversioned identifier catalog. See `src/shortcutforge/data/truth0530-LICENSE`.
- [Automators Talk iOS 16→17](https://talk.automators.fm/t/ios-16-17-new-and-updated-actions-and-backward-incompatibility/16523), [iOS 18→26.1](https://talk.automators.fm/t/ios-18-26-1-new-and-updated-actions/19029), [OS 26.2→26.4](https://talk.automators.fm/t/os-26-2-26-4-new-and-updated-actions/19117), and [OS 26.5→27 beta](https://talk.automators.fm/t/os-26-27-new-and-updated-actions/19177): community reports of named action/parameter changes, based on simulator and ToolKit databases. These are partial change lists, not complete per-version catalogs; platform limitations noted by the sources are retained.
- Detailed attribution is in `src/shortcutforge/data/NOTICE.md`.

## Commands

```sh
shortcutforge actions list --os 27 --format table
shortcutforge actions list --os 18 --query calendar
shortcutforge actions list --os 18 --query notification
shortcutforge actions list --os 27 --format json
shortcutforge actions list --os 26 --lang ja --format markdown --output ios26-actions.ja.md
```

For iOS 17/18/26, the OS selector scopes the requested candidate view; it does not transform unknown availability into support. Markdown localizes headings and the curated change list; action names remain in their source language. JSON output includes evidence and availability for manual evaluation. See the [English usage page](action-catalog.en.md) and [Japanese usage page](action-catalog.ja.md).

## How to improve older-version evidence

Export representative shortcuts from devices or simulators running each target iOS release, inspect their workflow plist identifiers and parameter dictionaries, and record the exact device OS/build with the extracted evidence. Keep “identifier observed,” “parameters observed,” and “runtime-tested” as separate evidence levels. See [the version-by-version verification status](action-compatibility.md); this repository has not performed physical-device checks for iOS 17, 18, 26, or 27.
