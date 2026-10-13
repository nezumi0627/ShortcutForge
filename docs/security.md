# Security model

ShortcutForge handles workflow definitions that can include personal data. Building and inspecting a file are local operations; signing dispatches data to GitHub and, if Apple's signing command reaches its validation service, to Apple. Do not use the current signing workflow for secrets or highly sensitive shortcut contents.

## Data boundaries

| Operation | Data handling |
| --- | --- |
| `build` | Reads a local JSON plan and writes a local plist. It does not execute actions or upload the plan. |
| `validate` / `inspect` | Reads a local plist; does not execute its workflow actions. |
| `actions list` | Reads the bundled catalog; does not need user data. |
| `sign` | Encodes the shortcut, stores it briefly as a uniquely named GitHub repository secret, dispatches the Apple signer workflow, and attempts to download its artifact. The runner uses a temporary directory and short artifact retention. Apple validation may receive the shortcut. RoutineHub HubSign is a separate third-party route that requires its own key/access and receives the shortcut contents. |

The signing client removes the temporary secret after the run. Cleanup is best effort if the process or network is interrupted; repository administrators can inspect and remove leftover secrets. The live GitHub-hosted runner test failed before producing a signed artifact because iCloud authentication was unavailable. See [signing validation](signing-validation.md).

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
