# Public template: first steps

ShortcutForge is a public GitHub template repository. Creating a repository from the template copies tracked source files and history according to GitHub's template behavior; it does not configure a signing environment or transfer the source repository's GitHub secrets.

## After creating a repository

1. Clone your new repository and install it with `python -m pip install -e .`.
2. Confirm `gh auth status` is logged into the account that owns the new repository.
3. Review `.github/workflows/` and set the repository's Actions policy to the minimum permissions needed for your use.
4. Run tests and create a synthetic `.shortcut` locally before using personal content.
5. Configure your own signing environment only after reading [signing validation](signing-validation.md) and [security](security.md).

## Signing is not ready on hosted macOS

The checked-in workflow documents the intended Apple signing command but the hosted macOS trial failed because iCloud sign-in is required. Do not assume that a template copy can sign unattended. A self-hosted Mac or another signing service requires separate setup, trust review, and validation; no credentials or signing identity are included in this template.

## Before publishing a release

Run the automated checks, inspect the package contents, ensure catalog attribution is present, update both README files and the changelog/release notes, and verify that no shortcut artifacts, secrets, or local data are staged. State which iOS/device combinations were actually tested.
