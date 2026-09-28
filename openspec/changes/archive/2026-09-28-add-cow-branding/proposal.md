# Proposal

## Why

The package has one official name, `custom-openspec-workflow`, but its human-facing surfaces do not identify the short name `COW` or the alias "chozian's OpenSpec Workflow". Users can encounter the project through the README, installer, command help, package metadata, or installed skill and miss that these names refer to the same project.

## What Changes

- Define `custom-openspec-workflow` as the official project name.
- Identify `COW` and "chozian's OpenSpec Workflow" as alternate names in human-facing package surfaces.
- Add a fuller identity statement near the start of `README.md`.
- Add brief identity text to package metadata, top-level CLI help, human-readable installer output, and the installed Grill skill.
- Add contract tests for the identity text and its placement in human-facing output.
- Keep command names, package imports, paths, environment-variable names, manifest data, and JSON output unchanged.
- Keep the existing `add-git-lifecycle-guidance` change separate and preserve its README content when both changes are applied.

## Capabilities

### New Capabilities

- `custom-openspec-branding`: Present the official project name and its alternate names consistently in human-facing package surfaces.

### Modified Capabilities

None.

## Impact

Implementation will update `README.md`, `pyproject.toml`, the public command help and human-readable installer text, the installed `custom-openspec-grill` skill, and related contract tests. It will not add dependencies, change machine-facing interfaces, modify OpenSpec policy behavior, or change user-level file ownership. The active Git lifecycle change also updates `README.md`, so implementation must preserve both sets of documentation changes.
