# Proposal

## Why

The current `custom-openspec-grill` skill describes how to stage and attach
Grill Me output, but it does not require the agent to run those commands.
Users must leave the AI session and run the helper script themselves. The
workflow also needs a clear order for Explore, optional Grill Me, and Propose.

OpenSpec Explore does not implement project code. The native skill can create
or update planning artifacts after the user confirms the files to change.
OpenSpec 1.13.2 has no supported guidance field for Explore. The package needs
a recommended no-write Explore convention so Propose remains the normal writer
of the initial planning artifacts, while documenting that the convention
cannot be enforced by OpenSpec configuration.

## What Changes

- Update the packaged `custom-openspec-grill` skill to:
  - Confirm that `.grill/` is ignored before it invokes Grill Me or stages a
    source.
  - Stop and tell the user to add `.grill/` to `.gitignore` when the directory
    is not ignored. The skill will not edit `.gitignore`.
  - Use the exact source path returned by Grill Me. Use source discovery only
    when exactly one plausible source exists. Ask the user when more than one
    source exists.
  - Run `custom-openspec-grill stage --source <source> --json` through the AI
    session and retain the returned session identity, source path, and
    repository root as a pending handoff.
  - Support the recommended flow of Explore discussion, optional Grill Me, and
    Propose. Keep Grill-first available for changes with high uncertainty.
  - Attach the pending session after Propose creates a named change and before
    Propose writes the initial planning artifacts.
  - Ask before using `--replace` or `--combine`.
  - Treat the source file and change-local `grill.md` as read-only snapshots.
    Record explicit user decisions in normal OpenSpec artifacts instead of
    rewriting the snapshots.
- Use the packaged OpenSpec policy to keep Grill context supplemental and to
  require the handoff before a normal planning artifact uses that context.
- Do not add Explore guidance. OpenSpec 1.13.2 does not support
  `operations.explore.guidance`, and the generated Explore skill remains
  unchanged.
- Document that Explore artifact writes after explicit confirmation are native
  OpenSpec behavior. They are outside the recommended Grill handoff path. The
  agent must not rewrite those artifacts automatically when Grill starts later.
  The user can use Update to reconcile them with attached Grill context.
- Update the README and skill contract tests to describe and check the
  recommended order, Git ignore preflight, decision precedence, native Archive
  behavior, and manual retention of external Grill files.
- Keep the upstream `grill-me` skill, its question process, the OpenSpec
  schema, and generated OpenSpec skills unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `custom-openspec-grill`: require safe source handling, agent-managed
  staging, pending session handoff, attachment before normal Propose planning,
  read-only snapshots, and explicit conflict and decision rules.

## Impact

The change affects:

- `src/custom_openspec_workflow/data/custom-openspec-grill/SKILL.md`.
- `src/custom_openspec_workflow/data/openspec-policy.yaml`.
- The Grill sections in `README.md`.
- Skill contract and workflow validation tests.

The existing Python staging and attachment API remains the implementation
boundary. The change does not edit `.gitignore` automatically, remove staged
sessions, or change native Archive behavior. The change does not modify the
upstream skill, OpenSpec source, generated OpenSpec skills, or the stock
artifact set.
