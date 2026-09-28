# Design

## Context

The project uses `setuptools>=68` to build a Python package. The package uses a `src` layout and declares its metadata in `pyproject.toml`.

The repository has no license file or license metadata. It includes project source, documentation, tests, fixtures, and a custom adapter skill. It does not copy the upstream Grill Me question process. The MIT notice applies to project-owned content only.

## Goals / Non-Goals

### Goals

- Make the root `LICENSE` file the source for the legal license text.
- Make package metadata identify the MIT License.
- Include the license file in built distributions.
- Make the license easy to find from `README.md`.
- Keep the current build-system minimum and runtime behavior.

### Non-Goals

- Add license headers to source files.
- Change commands, APIs, dependencies, or OpenSpec behavior.
- Change the license of external dependencies or upstream skills.
- Add a separate attribution or notice file.

## Decisions

### Use the standard MIT License text

Add the canonical MIT License text to `LICENSE`. Use `Copyright (c) 2026 Chris Hozian` in the notice. Do not add project-specific terms.

An edited license would add legal ambiguity without a stated need. A standard text gives users a known license with clear terms.

### Use file-backed package metadata

Add `license = { file = "LICENSE" }` to the `[project]` table. Add `license-files = ["LICENSE"]` to the existing `[tool.setuptools]` configuration.

This keeps the legal text in one file. The file form also works with the current `setuptools>=68` build requirement. A short license expression alone would not guarantee that the legal text is included in the distribution.

### Add a README license link

Add a short `License` section to `README.md` that links to `LICENSE`. Keep the section near the end of the document with other project-wide information.

The link improves discovery. It does not replace the license file or package metadata.

### Limit the notice to project-owned content

Describe the project license as applying to this repository's project-owned content. Do not claim ownership of external dependencies or upstream skills that the project only discovers or uses.

## Risks / Trade-offs

- [A distribution omits `LICENSE`] -> Set the explicit `license-files` option and inspect the built archive contents.
- [The metadata and license text diverge] -> Read the license text from the single root file and use the same file in package metadata.
- [Users misunderstand the scope of the notice] -> Link the README to the full license and state that external dependencies keep their own licenses.
- [A published release cannot be fully rolled back] -> Treat the license as permanent for copies distributed under it. Only use repository rollback before publication.

## Migration Plan

No runtime migration is required. Add the license file and metadata, update the README, run the existing test suite, and inspect a built source distribution or wheel for the license file and metadata.

If the change must be reverted before release, remove the new license section and metadata, then remove the unneeded license file. A release already distributed under the MIT License keeps the permissions granted to those copies.

## Open Questions

None. The copyright holder is `Chris Hozian`, and the notice year is 2026.
