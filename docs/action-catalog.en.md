# Apple Shortcuts action catalog

Before choosing actions, select the iOS version installed on the target device. Actions can be added, changed, or removed between iOS releases, so use the matching version catalog rather than assuming an action seen on another release is available:

```sh
shortcutforge actions list --os 26 --lang en --format markdown --output ios26-actions.md
```

Replace `26` with `17`, `18`, or `27`; use `--lang ja` for Japanese. Add `--query calendar` to narrow the list. The generated file contains the version change notes, identifiers, aliases/display names, evidence status, and source links.

The language setting translates headings and curated change notes. Action names are kept in the language supplied by the source, usually English, so they can be matched to the Shortcuts app and action identifiers.

## Version evidence

The full identifier list is not equally verified for every release. iOS 27 has 1,206 exact iOS 27 Simulator identifiers. Older releases currently use discovery candidates where exact-version evidence is not available. The change history below records named additions and changes reported for iOS 17, iOS 26.1/26.4, and iOS 27 beta; it does not imply every entry has an internal identifier or full parameter schema in this repository.

| Since | Evidence scope | Source |
|---|---|---|
| iOS 17 | Reported changes from iOS 16, including Clock, Files, Camera, cellular, and other actions | [Automators Talk](https://talk.automators.fm/t/ios-16-17-new-and-updated-actions-and-backward-incompatibility/16523) |
| iOS 26.1 | Reported changes from iOS 18.4; includes iOS and Mac-only entries, labeled in source | [Automators Talk](https://talk.automators.fm/t/ios-18-26-1-new-and-updated-actions/19029) |
| iOS 26.4 | Reported changes from iOS 26.2; platform-specific actions retained with notes | [Automators Talk](https://talk.automators.fm/t/os-26-2-26-4-new-and-updated-actions/19117) |
| iOS 27 beta | Reported changes from OS 26.5 to beta 4, plus an iOS 27 Simulator identifier snapshot | [Change notes](https://talk.automators.fm/t/os-26-27-new-and-updated-actions/19177), [identifier source](https://github.com/viticci/shortcuts-playground-plugin) |

Identifier presence is not a guarantee that the action works on a physical device or that its parameters are understood. If availability is unknown, check an exported shortcut or trusted source from the exact target version. Submit catalog corrections and additions as pull requests with evidence.
