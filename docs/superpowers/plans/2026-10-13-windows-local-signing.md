# Windows signer restriction and research plan

## Completed

- [x] Restrict Windows CLI signing to Shortcuty.
- [x] Remove the experimental iCloud-share retrieval path from the supported CLI.
- [x] Mark Windows-native, iPhone-assisted, and iCloud upload/retrieval alternatives as research-only in user documentation.
- [x] Add a CLI regression test that rejects non-Shortcuty signers on Windows.

## Research backlog

- [ ] Establish whether any Windows-native signing route can create a repeatably importable `.shortcut` without relying on unsupported private interfaces.
- [ ] Determine whether a supported Apple/iPhone-assisted workflow can be automated without exposing credentials or shortcut contents.
- [ ] Promote a method only after end-to-end iPhone import and execution validation.
