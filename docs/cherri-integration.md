# Cherri integration

ShortcutForge accepts `.cherri` source as an optional build input. It delegates compilation to the separate Cherri executable, always passes `--skip-sign`, validates the resulting workflow plist, and saves it at the requested output path. JSON plans remain the built-in, dependency-free path. The adapter does not translate Cherri syntax or implement Cherri's language; it is a bounded process wrapper.

## Install Cherri

Use Cherri's official installation instructions when possible. To build the current source yourself, install Go 1.24 or newer, then run:

```powershell
git clone https://github.com/electrikmilk/cherri.git
cd cherri
go build -o cherri.exe .
$env:PATH = "$PWD;$env:PATH"
```

Open a new terminal or add the directory containing `cherri.exe` to your user `PATH` permanently. Check availability with `cherri --help`. ShortcutForge does not download, bundle, or redistribute Cherri. Cherri is GPL-2.0 licensed; it remains a separate executable with its own release and support policy.

The upstream installation guide currently warns that Windows has been tried but is not supported reliably. ShortcutForge's Windows integration was smoke-tested by building the upstream compiler from source and compiling the included If/Repeat example. This confirms that one source/build combination works; it does not establish support for every Cherri feature, package, include, or upstream release. If native Windows compilation fails, install and configure WSL or use another environment supported by Cherri maintainers. ShortcutForge itself does not install or configure WSL.

## Choose between JSON and Cherri

Use JSON when the workflow fits ShortcutForge's named actions, when a compact data format is useful, or when you want to review the action list directly. Use Cherri when you want its language features, such as code-first If/Repeat structures or functions. The two paths have different schemas and validation guarantees:

| Input | Compiler | Validation boundary |
| --- | --- | --- |
| `PLAN.json` | ShortcutForge Python compiler | Plan schema, supported named action parameters, references, and plist-compatible values. |
| `SOURCE.cherri` | External Cherri executable | Process result and basic unsigned workflow plist structure. Cherri owns language parsing and action compilation. |

The action discovery catalog can inform either path, but a catalog entry does not prove that Cherri or iOS supports a particular action.

## Build and sign

```powershell
shortcutforge build examples/cherri-control-flow.cherri -o CherriExample.shortcut
shortcutforge validate CherriExample.shortcut
shortcutforge sign CherriExample.shortcut
```

`build` disables Cherri's own signing. The result is unsigned and must be signed before importing it into Shortcuts. On Windows, Shortcuty is the only enabled signer, so signing uploads the complete shortcut to Shortcuty's service. See [signing setup](signing-validation.md) before sending sensitive shortcut content. Cherri compilation itself runs locally; the separate signing command may transfer the workflow to a remote service.

The workflow name declared in the source becomes Cherri's `_unsigned.shortcut` intermediate filename. The adapter refuses to overwrite an existing intermediate, removes the intermediate after a successful or failed build, checks the plist structure, then writes the final build output. It does not execute the resulting shortcut or prove Apple action semantics. Keep the `.cherri` source and any included source files under your control; Cherri can process includes and packages.

If the executable is missing, add its containing directory to `PATH` and restart the terminal. If compilation fails, ShortcutForge reports the exit code without echoing compiler diagnostics; run Cherri directly in a trusted local terminal to view its detailed diagnostic. Inspect the resulting file with `shortcutforge validate` and `shortcutforge inspect` before deciding whether to sign it.

## References

- [Cherri source repository and license](https://github.com/electrikmilk/cherri)
- [Cherri installation and platform notes](https://cherrilang.org/install/)
- [Cherri language documentation](https://cherrilang.org/language/)
