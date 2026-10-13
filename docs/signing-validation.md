# Signing setup and validation

## Import requirement

**A `.shortcut` file must be signed before importing it as a file into Shortcuts on iPhone or iPad.** `build` writes an unsigned binary plist. `validate` checks structure only; it does not prove Apple will import or run the workflow.

## Default: Shortcuty (no API key)

```sh
shortcutforge sign BatteryDecisionLab.shortcut
```

The default sends the unsigned file to `https://sign.shortcuty.app/api/v1/sign?response=json`, then saves the signed file in the sibling `signed/` folder. Shortcuty's [API documentation](https://github.com/Shortcuty/Signing-Server-API-Documentation) says an API key is not required. ShortcutForge verifies the response's AEA1 format and both input and signed-file SHA-256 hashes before writing it. Shortcuty's [signer page](https://sign.shortcuty.app/) says uploaded files are kept only while signing.

This still uses a remote service: the complete shortcut is uploaded to Shortcuty. API-key-free does not mean offline. Do not use the default for secrets, private data, or sensitive workflows unless the transfer is authorized.

## Other signers

```sh
# RoutineHub HubSign: needs an API key and membership (unless an approved partner)
shortcutforge sign BatteryDecisionLab.shortcut --via hubsign

# Apple's local signer: Mac only, requires an iCloud-authenticated environment
shortcutforge sign BatteryDecisionLab.shortcut --via macos
```

HubSign reads `SHORTCUTFORGE_HUBSIGN_API_KEY` or prompts without echoing it. Do not put the key in command arguments, committed files, or chat. See the [RoutineHub API reference](https://routinehub.co/docs/api/), endpoint `POST /api/v1/sign-shortcut`.

Apple documents `shortcuts sign` for signing exported shortcuts and says Apple receives a copy for validation. ShortcutForge invokes:

```sh
shortcuts sign --mode anyone --input unsigned.shortcut --output signed.shortcut
```

The `anyone` mode allows anyone to import the shortcut. Apple also offers `people-who-know-me`, which restricts import to people who have the signer in their contacts and includes contact information in the file. ShortcutForge currently exposes `anyone` only.

## GitHub Actions and downloads

GitHub Actions are used for CI tests only. They do not sign or transport shortcut files. A specific signed example was published as a GitHub Release asset: [Download BatteryDecisionLab.signed.shortcut](https://github.com/nezumi0627/ShortcutForge/releases/download/battery-decision-lab-signed/BatteryDecisionLab.signed.shortcut).

## Validation limits

- The signer validates response format and checksums; that does not verify action semantics or guarantee import/runtime behavior.
- The nested If/Repeat sample has not been imported or run on a physical iPhone.
- Select the target iOS version before choosing actions. Catalog evidence is not a runtime guarantee.

## Sources

- [Shortcuty signer](https://sign.shortcuty.app/) and [API documentation](https://github.com/Shortcuty/Signing-Server-API-Documentation)
- [Apple: Run shortcuts from the command line](https://support.apple.com/guide/shortcuts-mac/apd455c82f02/mac)
- [Apple: Share shortcuts on Mac](https://support.apple.com/guide/shortcuts-mac/apdf01f8c054/mac)
- [RoutineHub API reference](https://routinehub.co/docs/api/)
