# Windows signing research status

## Current supported behavior

ShortcutForge supports Shortcuty as the only Windows signer. The default CLI command is `shortcutforge sign INPUT`; on Windows, selecting HubSign or the macOS signer is rejected.

## Research status

- Windows-native signing and direct iCloud share creation are not implemented.
- iPhone-assisted share/upload and signed-asset retrieval are exploratory research only.
- Reverse-engineered CloudKit requests and private Shortcuts APIs are not treated as supported interfaces.
- Re-enable an alternative only after a repeatable end-to-end procedure is verified on Windows and documented with its authentication and privacy requirements.
