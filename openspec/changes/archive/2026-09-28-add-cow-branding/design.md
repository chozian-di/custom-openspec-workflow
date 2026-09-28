# Design

## Context

The project uses `custom-openspec-workflow` in package metadata, command names, import paths, user-level paths, environment variables, and ownership data. Human-facing text is spread across `README.md`, three command parsers, installer output, package metadata, and the installed Grill skill. See `proposal.md` for the motivation and scope.

The repository also contains an untracked `add-git-lifecycle-guidance` change that updates `README.md`. The branding work must preserve that change and avoid editing its planning artifacts.

## Goals / Non-Goals

**Goals:**

- Present one consistent identity in human-facing package surfaces.
- Keep the official name `custom-openspec-workflow` visible.
- Introduce `COW` and "chozian's OpenSpec Workflow" without repeating long text in normal output.
- Keep the installer JSON contract and existing package identifiers stable.
- Make the identity easy to test and maintain.

**Non-Goals:**

- Do not rename commands, Python modules, package paths, environment variables, user-level directories, or manifest formats.
- Do not add a `cow` command or a second installation path.
- Do not add branding to `openspec-policy.yaml`, OpenSpec-generated skills, or upstream Grill Me content.
- Do not add branding fields to machine-readable installer output.

## Decisions

### Use display-only identity values

Add display-only project identity values beside the existing package constants. Use them for runtime help and human-readable installer text. Keep `PACKAGE_NAME` and all existing operational constants unchanged.

The package metadata and static installed skill cannot import runtime constants. Keep their short identity statements next to their existing descriptions and test the required phrases.

### Use one full statement in the README

Place the fuller identity statement near the start of `README.md`, before the package ownership explanation. This gives readers the official name and both alternate names once without adding repeated branding throughout the document.

### Keep other surfaces brief

Update top-level help for `custom-openspec-install`, `custom-openspec-init`, and `custom-openspec-grill` with a short identity reference. Add the same brief reference to human-readable installer plan, result, and refusal output. Keep JSON output unchanged.

Add one short attribution line to the installed `custom-openspec-grill` skill. Do not change the upstream skill name in front matter.

### Extend existing contract tests

Extend the existing README, skill, installer, and validation-matrix tests where they already inspect these surfaces. Add focused assertions for the official name, `COW`, the alternate name, and the absence of branding changes in JSON output. This avoids a separate test framework or a new test contract.

### Keep the active README change separate

Apply the branding edits to the current README content when implementation begins. Preserve the Git lifecycle section and its contract assertions from `add-git-lifecycle-guidance`. If both changes are applied in separate worktrees, merge the README sections without replacing either change.

### Alternatives considered

- Add the identity only to `README.md`. This does not help users who first see the installer or a host-loaded skill.
- Rename commands or paths to use `cow`. This would break scripts, existing installations, environment-variable names, and documentation.
- Add identity fields to JSON output. This would add human-facing data to a machine contract without a need.
- Repeat the full alias in every README section and every normal output line. This adds noise and makes future wording drift more likely.

## Risks / Trade-offs

- [Risk] The same identity can drift between Python, Markdown, and package metadata. -> Mitigation: use shared runtime display values where imports are available and add contract assertions for each static surface.
- [Risk] The active Git lifecycle change and this change both edit `README.md`. -> Mitigation: keep the changes separate in planning and preserve both sections during implementation.
- [Risk] `COW` can be unclear without its expansion. -> Mitigation: pair it with `custom-openspec-workflow` on first use and include the alternate name in the same identity statement.

## Migration Plan

No user migration is required. A normal package update changes only human-facing text and the installed skill content. The existing installer replaces managed files only under its current ownership rules. If a user changed a managed file, the installer keeps its existing conflict behavior.

To roll back, restore the previous package files and README text. No command, path, environment variable, manifest, or JSON migration is needed.

## Open Questions

None.
