# ShortcutForge documentation

Start with the README for installation and the shortest working example. These pages explain the details needed to build, inspect, extend, and safely contribute to the project.

## User guides

- [JSON plan format](json-plan-format.md): version 1 schema, action forms, parameters, and output references.
- [Action catalog: English](action-catalog.en.md) · [日本語](action-catalog.ja.md): search and render catalog entries for a selected iOS version.
- [Catalog sources and coverage](action-catalog-sources.md): provenance, evidence levels, and version gaps.
- [Signing setup and validation](signing-validation.md): available signers, Windows platform limits, data handling, and validation limits.
- [Battery Decision Lab](../examples/battery-decision-lab.json): nested If and Repeat raw-action example for iOS 27 research.
- [Template and release notes](template-and-release.md): public template setup and safe first steps.

## Project and contributor guides

- [Architecture](architecture.md): module boundaries, data flow, and design constraints.
- [Security model](security.md): untrusted inputs, secrets, workflows, artifacts, and public repository behavior.
- [Contributing](contributing.md): development setup, checks, and catalog PR evidence.
- [Agent instructions](../AGENTS.md): repository rules for humans and AI coding agents.

## Compatibility language

In this project, **observed** means a source snapshot contained an identifier or parameter. It does not mean the action imports or runs. **Unknown** means evidence is insufficient. **Runtime-tested** is reserved for an action exercised in the named Apple Shortcuts version and environment. See the [catalog evidence notes](action-catalog-sources.md).
