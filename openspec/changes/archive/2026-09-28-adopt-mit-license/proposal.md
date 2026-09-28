# Proposal

## Why

The repository does not state a license for its project-owned code and documentation. Users need clear permission to use, change, and share the project. This change adopts the MIT License for the project.

## What Changes

- Add a root `LICENSE` file with the standard MIT License text.
- Use `Copyright (c) 2026 Chris Hozian` in the license notice.
- Declare the MIT License in the Python package metadata.
- Add a license section to `README.md` that links to `LICENSE`.
- Keep runtime behavior, command names, and public interfaces unchanged.
- Keep external dependencies and upstream content under their own licenses.

## Capabilities

### New Capabilities

None. This change updates legal and package metadata surfaces. It does not add a runtime capability.

### Modified Capabilities

None. Existing behavioral requirements do not change.

## Impact

The change affects `LICENSE`, `pyproject.toml`, and `README.md`. Package metadata and built distributions will expose the MIT License. No source code, command behavior, dependency, or OpenSpec capability changes are required.
