# Contributing

Corrections and additions to the action catalog are welcome, as are focused fixes to the CLI, compiler, Skill, and documentation. Open an issue for a larger behavior change before investing in a broad implementation; small, well-scoped pull requests can go directly to review.

## Development setup

Requires Python 3.11 or newer. The JSON path has no runtime dependency outside the standard library. Cherri integration is optional and requires the separate Cherri executable; see the [integration guide](cherri-integration.md).

```sh
git clone https://github.com/nezumi0627/ShortcutForge.git
cd ShortcutForge
python -m pip install -e .
python -m unittest discover -s tests -v
```

For a direct source checkout without editable install, set `PYTHONPATH=src` before running the tests. On PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

## Action catalog contributions

Include as much of this evidence as applies:

1. Exact action identifier and any observed parameter keys/types.
2. Exact iOS version and build, plus device or simulator model/environment.
3. Source URL, exported workflow, or reproducible observation.
4. Evidence level: identifier observed, parameter observed, imported, or runtime-tested.
5. English and Japanese names/notes when adding curated display text.

Keep uncertainty explicit. A simulator identifier is not proof of physical-device support. A source catalog without a target OS is not exact version evidence. Update the source notes and attribution/license files when importing external data.

## Code and documentation changes

- Keep changes focused and typed; prefer standard-library solutions.
- Add or update tests for changed behavior. Do not label mocked workflow tests as live signing tests.
- Update both README entry points and relevant docs when commands, plan fields, APIs, limitations, or security behavior change.
- Never include personal shortcuts, `.shortcut` files, credentials, or real user data in commits or test fixtures.
- Use descriptive commit messages and explain user-visible behavior and evidence in the pull request.

## Before opening a pull request

```sh
python -m unittest discover -s tests -v
python -m compileall -q src
git diff --check
```

Then review the diff for stale compatibility statements, missing attribution, secrets, generated artifacts, and changes to workflow permissions or triggers. Follow [AGENTS.md](../AGENTS.md) and the [security model](security.md).
