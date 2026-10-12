# Action catalog data notices

`action_catalog.json` is a normalized index of public action identifiers and selected parameter metadata. It does not contain Apple runtime code or claim that every identifier works on every iOS release.

- Federico Viticci / MacStories, [shortcuts-playground-plugin](https://github.com/viticci/shortcuts-playground-plugin), MIT. Its ToolKit v78 iOS 27 Simulator identifier snapshot and parameter key/type snapshot were recorded on 2026-06-13. `viticci-LICENSE` contains the upstream license.
- carg, [mcp-server-ios-shortcuts](https://github.com/truth0530/mcp-server-ios-shortcuts), MIT. Its 415-entry catalog is unversioned; `truth0530-LICENSE` contains the upstream license.

The ToolKit v63 list (2026-02-09) has no declared OS/platform. It is retained as baseline discovery evidence, not labeled as iOS 26. No exact iOS 17, 18, or 26 snapshot is bundled. Their CLI views are candidate discovery results with availability marked `unknown`.

The normalized index retains per-record source URLs, observation dates, platform/runtime where supplied, and evidence kind. Parameter metadata is included only where the source marks it observed on iOS 27 Simulator. Identifiers and parameter keys may still be unavailable, changed, or semantically different on a physical device.
