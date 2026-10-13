# Security model

ShortcutForge handles workflow definitions that can include personal data. Building and inspecting a file are local operations. On Windows, Shortcuty is the only enabled signer and sends the shortcut to an external service without requiring an API key. HubSign and Apple's local Mac signer are available on supported non-Windows hosts. Do not send secrets or highly sensitive shortcut contents to remote signing services.

## Data boundaries

| Operation | Data handling |
| --- | --- |
| `build PLAN.json` | Reads a local JSON plan and writes a local plist. It does not execute actions or upload the plan. |
| `build SOURCE.cherri` | Starts the separately installed Cherri process locally with signing disabled. Cherri may read includes or packages referenced by the source; ShortcutForge does not upload the source during compilation. Review Cherri source and dependencies as code. |
| `validate` / `inspect` | Reads a local plist; does not execute its workflow actions. |
| `actions list` | Reads the bundled catalog; does not need user data. |
| `sign` (default) | Sends the unsigned shortcut to Shortcuty's signing service in a multipart HTTPS request. No API key is required. The returned AEA1 format and input/output SHA-256 checksums are verified before writing locally. |
| `sign --via hubsign` | Sends the shortcut and HubSign API key in a multipart HTTPS request to RoutineHub. The key is read from `SHORTCUTFORGE_HUBSIGN_API_KEY` or a concealed terminal prompt and is not placed in arguments or logs. |
| `sign --via macos` | Runs Apple's `shortcuts sign --mode anyone` locally on the user's Mac. Apple receives a copy for validation; the signed file is written locally. |

Shortcuty's signer page says uploaded files are kept only while signing. HubSign key setup and signing data recipients are documented in [signing validation](signing-validation.md). GitHub Actions are CI-only and do not receive shortcut payloads. Apple's local signer sends a copy to Apple for validation as Apple's documentation states.

## Public repository considerations

This repository is public. Treat source, issues, pull requests, workflow summaries, Actions run history and logs, and any artifact URL as public. GitHub explicitly makes Actions history and logs visible to everyone when a repository is made public ([visibility-change documentation](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)). Existing workflow artifacts may remain downloadable until their retention period expires. Do not put user shortcuts, sample personal data, tokens, or credentials in commits, issues, or pull requests. A repository secret is encrypted by GitHub, but workflows that can read it are part of the trusted computing base. Review workflow changes carefully.

Public pull request test workflows must use read-only permissions and must never receive signing secrets. Do not run untrusted pull request code in a privileged workflow. Keep actions permissions minimal, artifacts short-lived, and logs free of payload content. A public repository's template descendants do not receive its secrets; users must configure their own environment.

## Trust boundaries

- JSON plans and raw Apple action parameters are untrusted. The validator rejects unsupported fields/types and non-plist-compatible values; raw action semantics remain unknown.
- Catalog entries are evidence records, not executable schemas or compatibility guarantees.
- Workflow dispatch inputs, filenames, action metadata, and downloaded artifacts must be validated before use.
- `.shortcut` files are excluded from Git by `.gitignore`; verify staged changes before every commit.
- Never print, commit, or include payload values in exceptions. Report sanitized error context.

## Reporting a vulnerability

Do not post exploitable details or live shortcut payloads in a public issue. Use GitHub's private vulnerability reporting feature if enabled, or contact the repository owner through a private channel. Include the affected version/commit and a minimal reproduction with synthetic data.
