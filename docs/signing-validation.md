# Signing validation

## Status

**Blocked on Apple authentication.** On 2026-10-12 UTC, a synthetic shortcut was dispatched to GitHub-hosted `macos-14`. `/usr/bin/shortcuts sign --mode anyone` exited 1 with: `In order to do this, you must be signed into iCloud.` No Apple ID/iCloud login is available on the hosted runner. Therefore unattended signing on the requested stock hosted runner is not operational. Apple's command also emitted OS logging compatibility warnings, but the decisive error was missing iCloud sign-in.

The run's logs were deleted immediately after discovering GitHub printed the payload environment value. The workflow now uses a uniquely named, temporary GitHub Actions repository secret (automatically masked), removes it after the run, and correlates each run/artifact with a random nonce. This protects the payload from ordinary log output but still stores it briefly as an encrypted repository secret and sends it to Apple if signing reaches Apple's validation service.

Apple documents `shortcuts sign --mode anyone` and says Apple receives a copy for validation. A signed `.shortcut` was not produced. A supported path that keeps the Mac-free requirement is not established. Practical alternatives are signing on a Mac where the user is signed into iCloud, or using a carefully provisioned self-hosted Mac runner; a hosted runner with persistent Apple authentication would need separate security and reliability validation.

## Privacy

The client stores base64 shortcut bytes in a unique repository secret, dispatches the run, and removes the secret after completion. The workflow does not print the secret, signs in a temporary directory, removes that directory, and uploads a one-day artifact. Treat repository admins as trusted and do not use it for credentials or highly sensitive personal data. Apple validation receives the shortcut content.
