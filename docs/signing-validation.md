# Signing validation

## Status

Not yet live-verified. The project must run `.github/workflows/sign.yml` against a synthetic shortcut in the private repository and record the outcome here before claiming remote signing works. Apple documents `shortcuts sign --mode anyone` and says Apple receives a copy for validation. No claim is made here about whether GitHub-hosted macOS runners need an Apple account.

## Privacy

The workflow takes base64 shortcut bytes as a dispatch input, does not print them, signs in a temporary directory, removes that directory, and uploads a one-day artifact. Treat dispatch inputs as accessible to private-repository administrators and never use this workflow for credentials or sensitive personal data. Apple validation receives the shortcut content.
