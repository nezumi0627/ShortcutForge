# Signing setup and validation

## Import requirement

**A `.shortcut` file must be signed before importing it as a file into Shortcuts on iPhone or iPad.** `build` writes an unsigned binary plist. `validate` checks structure only; it does not prove Apple will import or run the workflow.

## Choose a signer

```sh
# Windows/Linux or any platform: RoutineHub HubSign (default)
shortcutforge sign BatteryDecisionLab.shortcut

# A Mac with Shortcuts and iCloud configured: Apple's local signer
shortcutforge sign BatteryDecisionLab.shortcut --via macos
```

`--via` selects the signing tool:

| Option | Runs where | Data sent | Requirements |
| --- | --- | --- | --- |
| `hubsign` (default) | Windows, macOS, Linux | HTTPS request to RoutineHub, including the shortcut and API key | HubSign API key and active RoutineHub membership unless approved as a partner client |
| `macos` | Local Mac only | Apple receives a copy for validation | macOS Shortcuts CLI and an Apple environment able to sign in to iCloud |

HubSign uses `SHORTCUTFORGE_HUBSIGN_API_KEY` or a concealed interactive prompt. Do not put the key in command arguments, files committed to Git, Actions secrets, or chat. Do not send shortcuts with sensitive data to a third party unless the user has authorized that transfer.

Apple documents `shortcuts sign` for signing exported shortcuts, and says Apple receives a copy for validation. ShortcutForge invokes:

```sh
shortcuts sign --mode anyone --input unsigned.shortcut --output signed.shortcut
```

The `anyone` mode allows anyone to import the shortcut. Apple also offers `people-who-know-me`, which restricts import to people who have the signer in their contacts and includes contact information in the file. ShortcutForge currently exposes `anyone` only.

## GitHub Actions

GitHub Actions are used for CI tests only. The signing and signed-artifact transport workflows have been removed: GitHub-hosted macOS did not provide the iCloud-authenticated Apple environment, and repository Actions should not receive user shortcut payloads. A previously successful signed artifact is available at [Actions artifact 11777771604](https://github.com/nezumi0627/ShortcutForge/suites/103817533071/artifacts/11777771604). This proves that this specific artifact was produced successfully; it does not validate this repository's local macOS signer or physical iPhone execution.

## Validation limits

- The signing commands verify the returned Apple-style `AEA1` header, not action semantics.
- The nested If/Repeat sample has not been imported or run on a physical iPhone.
- Select the target iOS version before choosing actions. Catalog evidence is not a runtime guarantee.

## Sources

- [Apple: Run shortcuts from the command line](https://support.apple.com/guide/shortcuts-mac/apd455c82f02/mac)
- [Apple: Share shortcuts on Mac](https://support.apple.com/guide/shortcuts-mac/apdf01f8c054/mac)
- [RoutineHub API reference](https://routinehub.co/v1/openapi.json), `POST /api/v1/sign-shortcut`
