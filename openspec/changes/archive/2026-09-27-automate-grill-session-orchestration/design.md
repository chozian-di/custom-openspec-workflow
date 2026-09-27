# Design

## Context

See `proposal.md` for the motivation. The existing adapter stages a source
outside the repository, writes session metadata, returns JSON, renders
traceable `grill.md` context, and attaches that context to a named change.

The current skill describes these operations but leaves execution to the user.
The source created by Grill Me can also remain visible to Git when a repository
does not ignore `.grill/`. OpenSpec 1.13.2 supports per-artifact rules and
advisory guidance for Apply and Archive. It does not support
`operations.explore.guidance`.

Native Explore is a thinking mode. It does not implement project code. It can
create or update planning artifacts after the user confirms the files to
change. This change uses a different convention for its normal Grill-to-
Propose path. Explore provides discussion and repository investigation. Propose
writes the initial planning artifacts.

The repository root already ignores `.grill/`. The skill still performs a
preflight for each target repository because the skill can run elsewhere.

## Goals / Non-Goals

Goals:

- Make the AI agent run the existing stage and attach operations.
- Recommend Explore discussion before Grill Me for normal changes.
- Keep Grill Me optional when Explore provides enough clarity.
- Keep Grill-first available for changes with high uncertainty.
- Keep Propose as the normal writer of the initial planning artifacts.
- Keep source selection safe when the upstream result does not provide an exact
  path.
- Confirm that `.grill/` is ignored before Grill Me creates or the adapter uses
  a source.
- Carry the session identity from Grill through Propose in the same AI session.
- Attach `grill.md` after a named change exists and before initial artifact
  writing.
- Keep source and change-local context as read-only snapshots during planning.
- Give the latest explicit user decision precedence over summaries and
  snapshots.
- Preserve idempotent attachment and explicit decisions for replacement or
  combination.
- Document native Archive behavior and manual retention of external files.
- Keep the existing shell commands available as a recovery path.

Non-goals:

- Do not change the upstream `grill-me` skill or its question process.
- Do not modify the generated OpenSpec Explore skill or add unsupported Explore
  guidance.
- Do not promise that OpenSpec prevents Explore from writing artifacts after
  explicit confirmation.
- Do not silently reconcile artifacts that Explore wrote before Grill ran.
- Do not modify `.gitignore` automatically.
- Do not modify OpenSpec generated skills or OpenSpec source.
- Do not add a replacement Propose command or a custom OpenSpec schema.
- Do not add automatic cleanup for `.grill/`, staged sessions, or archived
  copies.
- Do not add a cross-conversation pending-session registry in this change.
- Do not choose a source or change by timestamp, generated slug, or arbitrary
  ordering.

## Decisions

### Recommend Explore before Grill Me

The normal package flow is:

1. Use Explore for discussion and repository investigation.
2. If the requirements are clear, continue to Propose without Grill Me.
3. If important requirements remain unresolved, run `custom-openspec-grill`.
4. Keep the returned session identity as a pending handoff.
5. Run Propose. After Propose creates the named change, attach the pending
   session before Propose writes the initial planning artifacts.
6. Continue with normal OpenSpec planning.

Grill-first remains a supported alternative for changes with high uncertainty.
The user can run Grill Me, then use Explore to test the captured decisions
against the repository, and then use Propose.

This order keeps the deeper Grill session focused. It also lets users skip
Grill Me when Explore provides enough clarity.

### Define the native Explore boundary

The installed Explore skill prohibits implementation work. It permits confirmed
writes to planning artifacts. This change does not modify that skill because
OpenSpec 1.13.2 does not expose `operations.explore.guidance`.

The package README and policy will recommend that Explore remain discussion-only
before Propose in the normal workflow. Propose remains the normal initial
artifact writer. This is an agent convention, not a native OpenSpec guarantee.

If a user explicitly authorizes Explore to write a planning artifact before
Grill runs, the package does not rewrite that artifact when Grill starts later.
The agent reports that the artifact predates Grill context. The user can use
OpenSpec Update after attachment when the artifact needs reconciliation.

Modifying the generated Explore skill is rejected because OpenSpec can
regenerate it and the supported configuration does not provide an Explore
guidance field.

### Use the packaged adapter skill as the orchestrator

Update `src/custom_openspec_workflow/data/custom-openspec-grill/SKILL.md`. The
skill will use this order after the user chooses Grill Me:

1. Confirm that `.grill/` is covered by Git ignore rules. If it is not
   ignored, stop and tell the user to add the rule. Do not edit `.gitignore`.
2. Find the installed upstream `grill-me` skill and delegate the requirements
   session. The adapter will not copy the upstream question process.
3. Use the exact source path from the upstream result when it is available.
   If the result has no path, inspect plausible sources only when one source
   exists. Ask the user when more than one source exists.
4. Run `custom-openspec-grill stage --source <source> --json` through the AI
   session.
5. Record the returned repository root, source path, staging directory, and
   `sessionId` as a pending handoff in the active AI session.
6. If Propose has not created a named change, keep the pending handoff while
   the user completes discussion.
7. When Propose creates the named change, run
   `custom-openspec-grill attach --root <repository> --change <change-name>
   --session <session-id> --json` before the first initial planning artifact
   is written.

The skill will ask the user to select a source or change when selection is
ambiguous. It will ask before it passes `--replace` or `--combine`.

The alternative is to make the user run the shell commands. That keeps the
skill shorter but breaks the handoff across Grill and planning work. The
pending handoff keeps the existing two-step API and solves the timing problem
between staging and Propose.

### Use existing CLI state and safety

The skill will call the existing `stage` and `attach` operations. The stage
operation remains responsible for stable session identity and external staging.
The attach operation remains responsible for source traceability, required
context sections, idempotence, and existing-context conflicts.

The skill will use JSON output. It will pass `--root` to attachment so the
operation does not depend on the process working directory. It will pass the
session identity returned by staging instead of reconstructing an identity from
a filename.

The alternative is to add a second state store in the skill. That duplicates
session metadata and creates another source of truth. The existing staging
metadata remains authoritative, while the active AI session retains only the
pending handoff needed to continue.

### Protect source and attached snapshots

The source under `.grill/` and the change-local `grill.md` are historical
snapshots. The stage operation reads the source. The attach operation renders a
change-local copy. Planning work reads both files and does not edit either
file.

An explicit user decision takes precedence over a conflicting summary or
snapshot. If the user changes a decision later, the latest explicit decision
wins whether the decision comes from Explore or Grill. The agent records the
active decision in `proposal.md`, `design.md`, or the relevant specification.
The snapshots remain unchanged.

The alternative is to rewrite `grill.md` after every planning decision. That
removes the source history and makes it unclear which decisions came from
Grill and which decisions came later.

### Use supported policy surfaces

Update `src/custom_openspec_workflow/data/openspec-policy.yaml` so proposal,
specification, design, and task guidance requires a pending Grill handoff
before a normal planning artifact uses Grill context. The guidance will state
that Grill context is supplemental and that the latest explicit user decision
wins.

The policy will not add `operations.explore.guidance` because the supported
OpenSpec version does not read that field. It cannot enforce the recommended
no-write Explore convention. The generated Explore skill remains unchanged.

The alternative is to modify the generated Explore skill. That is outside the
supported extension point and the change would disappear when OpenSpec
regenerates its skills.

### Preflight the Git ignore rule

The packaged skill will inspect the target repository's Git ignore rules
before it invokes Grill Me or stages a source under `.grill/`. If the check
fails, the skill will stop and tell the user to add `.grill/` to
`.gitignore`. It will not edit the file automatically.

The alternative is to add the rule during the workflow. That changes a user
repository without an explicit request and can hide an existing repository
policy problem.

### Preserve Archive behavior and use manual retention

Native Archive moves the complete named change directory. Because
change-local `grill.md` is inside that directory, it moves to
`openspec/changes/archive/<date>-<change>/grill.md` with the other artifacts.
The source under `.grill/` and the staged session under the user-level data
directory are outside the change directory. Archive leaves them in place.

The package will document manual retention and removal. It will not delete
source or staged files after attachment or Archive.

The alternative is automatic cleanup after attachment or Archive. That removes
recovery material and can delete a source the user wants to retain.

### Test the contract at the skill boundary

Update the skill contract tests to check:

- The Git ignore preflight and the instruction to stop without editing
  `.gitignore`.
- Agent execution of both operations.
- JSON output and explicit root, change, and session arguments.
- Exact-source preference and source ambiguity questions.
- Pending session retention and attachment before Propose's initial artifacts.
- The recommended Explore-first order and the Grill-first alternative.
- The native Explore write limitation and the no-rewrite rule for prior
  artifacts.
- Latest explicit decision precedence.
- Change ambiguity and conflict safeguards.
- No changes to the upstream question process or generated Explore skill.

Keep the existing staging and attachment tests as the behavioral tests for the
Python adapter. Add focused adapter coverage only if a changed contract is not
already covered. Add README and policy assertions for the documented order,
handoff, ignore preflight, Archive behavior, and manual retention.

## Risks / Trade-offs

- [The repository does not ignore `.grill/`] -> Stop before Grill Me or staging
  and give the user the exact ignore rule to add.
- [Explore writes an artifact before Grill runs] -> Do not claim that the
  artifact used Grill context. Preserve it and use OpenSpec Update when the
  user wants reconciliation.
- [The user expects native OpenSpec to block Explore writes] -> Explain that
  the no-write rule is a package convention because OpenSpec has no supported
  Explore guidance field.
- [The upstream result does not expose a source path] -> Inspect only
  plausible source material in the current repository. Ask the user when more
  than one source exists.
- [The active AI session ends before Propose] -> Keep the staged source and
  session metadata unchanged. Leave the manual attach command as a recovery
  path.
- [A repository has several active changes] -> Ask the user to select the
  target change. Never attach to an arbitrary change.
- [A later explicit decision conflicts with Grill] -> Record the latest explicit
  user decision in the normal planning artifact and keep both snapshots
  unchanged.
- [External copies remain after Archive] -> Document the locations and make
  removal a manual user action.
- [An existing change already contains Grill context] -> Preserve the file and
  ask for an explicit replacement or combination decision.

## Migration Plan

1. Install the updated package so the new packaged skill reaches
   `~/.agents/skills/custom-openspec-grill/SKILL.md`.
2. Use Explore for discussion before Grill Me for normal changes. Use Grill
   first when the change has high uncertainty.
3. If Grill runs, use the new skill to stage the source and retain the pending
   handoff until Propose.
4. Existing staged sessions keep their current metadata and remain attachable.
5. Remove old source or staged files manually when the user no longer needs
   them.

To roll back, reinstall the previous package version. The change does not
modify staged session data or require a repository migration.
