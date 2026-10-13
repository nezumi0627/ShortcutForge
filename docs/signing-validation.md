# Signing setup and validation

## Import requirement

**A `.shortcut` file must be signed before importing it as a file into Shortcuts on iPhone or iPad.** `build` writes an unsigned binary plist. `validate` checks only its structure; it does not sign the file or prove that Apple will import or run it.

## Recommended: RoutineHub HubSign

`shortcutforge sign FILE` sends an unsigned workflow to RoutineHub's HubSign API and saves the returned signed file at `FILE`'s sibling `signed/` directory. The API requires a separate HubSign API key and active RoutineHub membership, unless the caller is an approved partner client. See the [official API reference](https://routinehub.co/v1/openapi.json), endpoint `POST /api/v1/sign-shortcut`.

Provide the key without putting it in command arguments or a plan:

```powershell
shortcutforge sign .\BatteryDecisionLab.shortcut
```

In an interactive terminal, `shortcutforge sign FILE` also prompts for the key without echoing it. On a non-interactive runner, set `SHORTCUTFORGE_HUBSIGN_API_KEY` through that runner's secret manager. Never commit the key. The command checks that the input is a Shortcuts workflow plist and that the response begins with HubSign's signed-file header (`AEA1`) before saving it.

**Privacy:** HubSign receives the full shortcut file and the API key in an HTTPS form request. Do not send shortcuts containing passwords, authentication tokens, private medical/financial details, or other sensitive content. Successful signing in this repository was recorded on 2026-10-12 in [Actions run 38319254307](https://github.com/nezumi0627/ShortcutForge/actions/runs/38319254307); the downloaded file had the signed `AEA1` header. This is evidence of a successful HubSign response, not an iPhone runtime test.

## Optional fallback: Apple signing on GitHub-hosted macOS

Use `shortcutforge sign FILE --via github-actions` only when explicitly selecting the Apple workflow. On 2026-10-12 and again on 2026-10-13, `/usr/bin/shortcuts sign --mode anyone` on GitHub-hosted `macos-14` exited with `In order to do this, you must be signed into iCloud.` The workflow uploaded an unsigned fallback artifact after the Apple command failed. It did not produce a signed file. A Mac signed into iCloud may be used manually; self-hosting an authenticated runner needs separate security and reliability review.

The GitHub fallback stores the base64 file briefly in a unique repository secret, removes it after the run, and retains the artifact for one day. Repository admins and GitHub receive the workflow payload. Apple's validation service may also receive the shortcut if the command reaches that step. See [security and data handling](security.md).

## Validation limits

- The HubSign command's automated check verifies the returned signed-file header, not its action semantics.
- The sample with nested If and Repeat blocks has not been imported or run on a physical iPhone.
- Select the target iOS version before selecting actions. Versioned catalog evidence is not a runtime guarantee.
