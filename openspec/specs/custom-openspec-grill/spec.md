# custom-openspec-grill Specification

## Purpose

This capability adds optional requirements interrogation to OpenSpec through the upstream Grill Me skill. It surfaces user intent, hidden assumptions, constraints, decisions, ambiguities, tradeoffs, non-goals, and unresolved questions. It produces traceable supplemental planning context without replacing OpenSpec Explore or changing the stock artifact set.

## Requirements

### Requirement: Delegate requirements interrogation

`custom-openspec-grill` SHALL delegate the question process to the installed upstream Grill Me skill from `satya-janghu/agent-skills`. It MUST NOT copy, fork, or replace Grill Me interrogation logic, and it MUST perform no implementation work.

#### Scenario: Grill Me is available

- **WHEN** a user starts an OpenSpec Grill session
- **THEN** the adapter invokes the upstream Grill Me skill, allows its normal question process, and waits for its distilled result before producing OpenSpec context

#### Scenario: Grill Me is unavailable

- **WHEN** the adapter cannot find the configured upstream Grill Me skill
- **THEN** it reports the missing dependency, identifies the checked user-level skills location, directs the user to install `skills/grill-me` from `satya-janghu/agent-skills`, references the package README, performs no implementation work, and leaves existing Grill source material unchanged

#### Scenario: Grill is skipped

- **WHEN** a change is trivial or already sufficiently specified
- **THEN** the user can continue with normal OpenSpec Explore or Propose without running the adapter

### Requirement: Produce supplemental Grill context

After a completed Grill Me session, the adapter SHALL produce or import a change-linked `grill.md` document. It SHALL preserve these sections:

- Intent.
- Constraints.
- Decisions.
- Assumptions Surfaced.
- Open Questions.
- Non-Goals or Out of Scope.

The document SHALL distinguish resolved decisions from unresolved questions and SHALL preserve the source identity needed for traceability. It SHALL retain relevant tradeoffs and ambiguities in the appropriate sections or supplemental notes without presenting unresolved items as decisions.

#### Scenario: Grill session produces context

- **WHEN** the upstream Grill Me session completes
- **THEN** the resulting context contains all required sections and preserves confirmed intent, constraints, decisions, surfaced assumptions, open questions, and non-goals

#### Scenario: Grill output has unresolved questions

- **WHEN** the distilled Grill result contains unresolved questions
- **THEN** `grill.md` records them as open questions and does not present them as resolved decisions

### Requirement: Stage Grill results before a change exists

When no OpenSpec change exists, the adapter SHALL retain the Grill source
material in a non-root staging location and assign or preserve a stable session
identity. It MUST NOT create an unrelated root-level `grill.md` or a custom
OpenSpec schema artifact. When the user does not provide an explicit staging
directory, the adapter SHALL use
`~/.local/share/custom-openspec-workflow/grill/` unless
`CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME` provides another location.

The package SHALL recommend that the user start with Explore discussion. If
Explore does not resolve the requirements, the user can run the
`custom-openspec-grill` skill before Propose. The skill can also run before
Explore when a change has high uncertainty.

Before it invokes Grill Me or uses a source under the repository's
`.grill/` directory, the `custom-openspec-grill` skill SHALL confirm that
`.grill/` is covered by Git ignore rules. If the directory is not ignored, the
skill SHALL stop and tell the user to add `.grill/` to `.gitignore`. It MUST
NOT edit `.gitignore`, stage the source, or attach a session.

After a completed Grill Me session, the skill SHALL identify the exact source
returned by Grill Me and perform the staging action through the AI session. If
the upstream result does not identify a source, the skill SHALL use source
discovery only when one plausible source exists. It MUST ask the user to
select a source when more than one plausible source exists and MUST NOT select
a source only because it has the newest timestamp or a generated filename.

After the upstream session returns, the source under `.grill/` SHALL be
treated as a read-only snapshot. The skill MUST NOT edit or delete it while it
stages or hands off the session.

The skill SHALL retain the staged session identity, source path, and repository
root as a pending handoff until the session is attached to a named change or
the user chooses not to continue with the change.

#### Scenario: Explore resolves the requirements without Grill

- **WHEN** Explore discussion provides enough clarity for the user to continue
  and the user does not run the Grill skill
- **THEN** the user can continue to Propose without a staged Grill session

#### Scenario: User grills before proposal creation

- **WHEN** Explore discussion leaves important requirements unresolved and the
  user runs the Grill skill before Propose
- **THEN** the skill stages the exact Grill source outside the repository,
  reports the stable session identity, and retains the identity for Propose

#### Scenario: User grills before Explore

- **WHEN** the user runs the Grill skill before Explore for a high-uncertainty
  change
- **THEN** the skill stages the exact Grill source outside the repository and
  retains the identity for later planning

#### Scenario: The default staging location is used

- **WHEN** the user stages a source without an explicit staging directory or
  environment override
- **THEN** the adapter stores the session under
  `~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/`

#### Scenario: The user selects a staging location

- **WHEN** the user provides `--staging-dir` or sets
  `CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME`
- **THEN** the adapter uses the selected location instead of the default
  staging location

#### Scenario: The Grill directory is not ignored

- **WHEN** the repository's `.grill/` directory is not covered by Git ignore
  rules
- **THEN** the skill stops before staging, tells the user to add `.grill/` to
  `.gitignore`, leaves `.gitignore` unchanged, and does not attach a session

#### Scenario: The Grill source remains unchanged

- **WHEN** the skill stages and later attaches a source from `.grill/`
- **THEN** the source snapshot remains unchanged and the skill does not delete
  it as part of the handoff

#### Scenario: Grill source uses a generated slug

- **WHEN** the upstream source is named with a generated filename slug
- **THEN** later attachment uses the stable session identity and source
  traceability instead of relying only on that slug

#### Scenario: One fallback source exists

- **WHEN** the upstream result does not provide a source path and source
  discovery finds exactly one plausible source
- **THEN** the skill stages that source without asking the user to repeat the
  selection

#### Scenario: Multiple fallback sources exist

- **WHEN** the upstream result does not provide a source path and source
  discovery finds more than one plausible source
- **THEN** the skill asks the user to select the source and does not stage a
  source before the selection

### Requirement: Attach staged context to a change

When an OpenSpec change exists, the adapter SHALL place `grill.md` with that
change or create an equally unambiguous documented relationship to the change.
The relationship SHALL preserve the source session identity and source
traceability. It MUST NOT depend only on a fragile filename slug.

In the recommended flow, the `custom-openspec-grill` skill SHALL attach a
pending staged session after Propose creates a named change and before Propose
writes `proposal.md` or any other initial planning artifact. The agent SHALL
retain the session identity between staging and this attachment.

If a named change already exists when a pending session becomes available, the
skill SHALL attach it before the next planning artifact that uses Grill
context. It MUST NOT rewrite earlier artifacts automatically because they
predate the Grill session.

The attach command SHALL include `--root <repository>`,
`--change <change-name>`, `--session <session-id>`, and `--json`. When exactly
one applicable named change exists, the skill SHALL select it automatically.
When more than one applicable named change exists, the skill MUST ask the user
to select the change before attachment.

#### Scenario: User attaches a staged session

- **WHEN** Explore discussion is complete, a pending staged Grill session
  exists, and Propose creates a named change
- **THEN** the skill attaches the session before Propose writes the first
  planning artifact, and the change contains `grill.md` or its documented
  equivalent

#### Scenario: Grill-first planning attaches a pending session

- **WHEN** Grill runs before Explore and a pending session exists when Propose
  creates a named change
- **THEN** the skill attaches the session before Propose writes the first
  planning artifact

#### Scenario: A named change already exists

- **WHEN** a pending Grill session becomes available after a named change
  already contains planning artifacts
- **THEN** the skill preserves the earlier artifacts, attaches the session
  before the next Grill-dependent artifact, and does not claim that earlier
  artifacts used Grill context

#### Scenario: One named change exists

- **WHEN** a pending staged session exists and exactly one applicable named
  OpenSpec change exists
- **THEN** the skill attaches the session to that change without asking the
  user to repeat the change name

#### Scenario: Multiple named changes exist

- **WHEN** a pending staged session exists and more than one applicable named
  OpenSpec change exists
- **THEN** the skill asks the user to select the target change and does not
  attach the session before the selection

#### Scenario: Change-local context already exists

- **WHEN** the selected change already has Grill context for a different
  session
- **THEN** the adapter preserves the existing context and requests an explicit
  user decision before replacement or combination

#### Scenario: Replacement or combination is requested

- **WHEN** a change already has Grill context and the user has not explicitly
  selected replacement or combination
- **THEN** the skill does not use `--replace` or `--combine`

#### Scenario: Attachment is repeated

- **WHEN** the user attaches the same staged session more than once
- **THEN** the adapter does not create ambiguous duplicate context and reports
  the existing attachment

### Requirement: Treat Grill context as supplemental planning input

When applicable change-linked `grill.md` context exists, OpenSpec proposal,
specification, design, and task work SHALL use its confirmed intent,
constraints, decisions, resolved assumptions, non-goals, and open questions as
supplemental planning input. The context SHALL remain separate from the stock
OpenSpec artifact set.

The package SHALL recommend the following normal planning flow:

1. Use Explore for discussion and repository investigation.
2. If important requirements remain unresolved, run the Grill skill.
3. Use Propose as the normal writer of the initial planning artifacts.
4. Attach a pending Grill session after the named change exists and before the
   initial artifacts are written.

The native Explore skill does not implement project code. It can create or
update planning artifacts after the user confirms the files to change. OpenSpec
1.13.2 does not provide a supported Explore guidance field that can prevent
those writes. Such Explore artifact writes are outside the recommended
Grill-to-Propose handoff path.

If Explore writes artifacts before Grill runs, the skill MUST NOT rewrite them
automatically or claim that they used Grill context. The user can use OpenSpec
Update to reconcile those artifacts after attachment.

An explicit user decision SHALL take precedence over a conflicting summary or
snapshot. If the user explicitly changes a decision later, the latest explicit
decision wins, whether the decision comes from Explore or Grill. The agent
SHALL record the active decision in the applicable normal OpenSpec artifact. It
MUST NOT rewrite the source snapshot or change-local `grill.md` to make the
records agree.

The native Archive workflow SHALL move the complete named change, including
`grill.md`, to
`openspec/changes/archive/<date>-<change>/grill.md`. Archive SHALL leave the
repository's `.grill/` source and user-level staged sessions outside the
archive. Cleanup of those external files SHALL remain a manual user action.

#### Scenario: Explore remains discussion-only in the normal flow

- **WHEN** the user uses Explore before Propose and does not explicitly
  authorize planning-artifact capture
- **THEN** Explore records discussion in the active AI session and Propose
  remains the normal writer of the initial planning artifacts

#### Scenario: Proposal uses attached Grill context

- **WHEN** a pending Grill session is attached before Propose writes the
  initial artifacts
- **THEN** the artifacts retain relevant confirmed decisions and non-goals,
  and the change still uses the stock OpenSpec artifact set

#### Scenario: Explore artifact capture is explicit

- **WHEN** the user explicitly authorizes Explore to create or update planning
  artifacts before Grill runs
- **THEN** native Explore can write those artifacts, and the package does not
  claim that the artifacts used Grill context

#### Scenario: User runs Grill after Explore discussion

- **WHEN** Explore discussion leaves important requirements unresolved and the
  user runs Grill before Propose
- **THEN** the pending session remains available for attachment before Propose
  writes the initial artifacts

#### Scenario: A later explicit decision changes context

- **WHEN** the user explicitly changes a decision after an earlier decision from
  Explore or Grill
- **THEN** the latest decision appears in the applicable OpenSpec artifact, and
  the source snapshot and change-local `grill.md` remain unchanged

#### Scenario: Archive preserves change-local context

- **WHEN** the named change is archived through native OpenSpec Archive
- **THEN** the complete change moves to the dated archive path and retains
  `grill.md`

#### Scenario: Archive does not clean external context

- **WHEN** native OpenSpec Archive completes
- **THEN** the source under `.grill/` and the user-level staged session remain
  in their existing locations until the user removes them

#### Scenario: No Grill context exists

- **WHEN** a change has no applicable `grill.md` or pending Grill session
- **THEN** normal OpenSpec proposal, specification, design, and task work
  remains available without a forced Grill step

### Requirement: Keep the adapter independently upgradeable

The adapter SHALL depend on the smallest practical public behavior contract of Grill Me. It MUST avoid brittle assumptions about exact prompts, line positions, prose, or filename slug formatting. It SHALL discover the installed dependency and MUST NOT invent a fixed Grill Me revision when the target requires compatibility with the installed skill. It SHALL provide a compatibility check for upstream Grill Me changes. The documented compatibility check SHALL report actual dependency, required-section, pre-change staging, change attachment, repeated-attachment, source-traceability, optional-use, and no-implementation-work evidence from isolated state. It MUST NOT claim delegation or implementation status from hard-coded success values.

#### Scenario: Grill Me output structure changes

- **WHEN** an upstream Grill Me update changes output wording or structure without removing its meaning
- **THEN** the adapter uses semantic extraction or reports a clear compatibility result instead of relying on fixed line positions or exact prose

#### Scenario: User tests a Grill Me update

- **WHEN** the user runs the documented Grill Me compatibility test
- **THEN** the test discovers the installed `grill-me` skill, exercises staging and attachment in disposable state, confirms repeated attachment is idempotent, checks required context sections and source traceability, confirms the optional path remains available, and reports that no implementation work occurred

#### Scenario: Compatibility evidence is unavailable

- **WHEN** the installed Grill Me skill or an adapter contract check is unavailable
- **THEN** the compatibility test reports the missing evidence with an actionable failure and leaves the target repository, staged source, and upstream Grill Me skill unchanged

### Requirement: Explain a missing Grill Me dependency

When the `custom-openspec-grill` wrapper cannot find the upstream `grill-me`
skill, it SHALL report the checked user-level skills directory and state that
Grill cannot run until the skill is installed. The message SHALL direct the
user to install `skills/grill-me` from `satya-janghu/agent-skills` and read the
package README for host-specific instructions.

The wrapper SHALL stop the Grill operation without installing or changing the
upstream skill or existing Grill source material. Missing Grill Me SHALL not
prevent normal OpenSpec Explore or Propose work.

#### Scenario: Grill Me is missing

- **WHEN** a user starts the Grill wrapper and `grill-me/SKILL.md` is not in
  the selected skills directory
- **THEN** the wrapper reports the checked directory, the missing dependency,
  the installation source and path, and the README reference, then stops
  without changing source material

#### Scenario: Grill Me is available

- **WHEN** the selected skills directory contains the upstream `grill-me`
  skill
- **THEN** the wrapper continues with normal delegation and does not report a
  missing dependency

#### Scenario: Grill is skipped

- **WHEN** the user continues with normal OpenSpec work without Grill
- **THEN** missing Grill Me does not block Explore or Propose
