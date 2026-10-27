# Action catalog data notices

`action_catalog.json` is a normalized index of public action identifiers and selected parameter metadata. It does not contain Apple runtime code or claim that every identifier works on every iOS release.

- Federico Viticci / MacStories, [shortcuts-playground-plugin](https://github.com/viticci/shortcuts-playground-plugin), MIT. Its ToolKit v78 iOS 27 Simulator identifier snapshot and parameter key/type snapshot were recorded on 2026-06-13. `viticci-LICENSE` contains the upstream license.
- `action_names.json` contains source-provided English display names for first-party actions observed on iOS 27 Simulator, from the same project's ToolKit v78 parameter snapshot.
- carg, [mcp-server-ios-shortcuts](https://github.com/truth0530/mcp-server-ios-shortcuts), MIT. Its 415-entry catalog is unversioned; `truth0530-LICENSE` contains the upstream license.
- pfgithub / Cavin Graves, [scpl-macos-updated](https://github.com/cavingraves/scpl-macos-updated), v2.3.1, MIT. `scpl_macos_2.3.1_outactions.json` is the pinned upstream source snapshot. `scpl_ios27_actions.json` contains 282 schemas whose identifiers were observed in the ToolKit v78 iOS 27 simulator snapshot and whose source parameter keys all appear in its parameter snapshot; 43 candidates with unobserved keys are explicitly excluded. `tools/generate_sourced_actions.py` reproduces the filtered catalog. `SCPL-MIT-LICENSE` contains the upstream license. These checks do not establish iOS 17/18/26 compatibility or iPhone runtime behavior.
- Named version-change notes include user-facing additions from Apple's official release notes and partial action/parameter comparisons from [Automators Talk](https://talk.automators.fm/). Community reports describe simulator/ToolKit database comparisons and explicitly note incomplete simulator coverage. Neither source type establishes a complete internal-ID and parameter catalog for each release.

The ToolKit v63 list (2026-02-09) has no declared OS/platform. It is retained as baseline discovery evidence, not labeled as iOS 26. No exact iOS 17, 18, or 26 snapshot is bundled. Their CLI views are candidate discovery results with availability marked `unknown`.

The normalized index retains per-record source URLs, observation dates, platform/runtime where supplied, and evidence kind. Parameter metadata is included only where the source marks it observed on iOS 27 Simulator. Identifiers and parameter keys may still be unavailable, changed, or semantically different on a physical device.
