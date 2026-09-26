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

#### Scenario: User grills before proposal creation

- **WHEN** the user runs the adapter before an OpenSpec change exists
- **THEN** the adapter retains the source in the documented non-root staging area and reports a stable identity that can be attached to a later named change

#### Scenario: The default staging location is used

- **WHEN** the user stages a source without an explicit staging directory or environment override
- **THEN** the adapter stores the session under `~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/`

#### Scenario: The user selects a staging location

- **WHEN** the user provides `--staging-dir` or sets `CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME`
- **THEN** the adapter uses the selected location instead of the default staging location

#### Scenario: Grill source uses a generated slug

- **WHEN** the upstream source is named with a generated filename slug
- **THEN** later attachment uses the stable session identity and source traceability instead of relying only on that slug

### Requirement: Attach staged context to a change

When an OpenSpec change exists, the adapter SHALL place `grill.md` with that change or create an equally unambiguous documented relationship to the change. The relationship SHALL preserve the source session identity and source traceability. It MUST NOT depend only on a fragile filename slug.

#### Scenario: User attaches a staged session

- **WHEN** the user attaches a staged Grill session to a named OpenSpec change
- **THEN** the change contains `grill.md` or its documented equivalent, and the context identifies the source session without relying only on its generated filename

#### Scenario: Change-local context already exists

- **WHEN** the selected change already has Grill context
- **THEN** the adapter preserves the existing context and requests an explicit user decision before replacement or combination

#### Scenario: Attachment is repeated

- **WHEN** the user attaches the same staged session more than once
- **THEN** the adapter does not create ambiguous duplicate context and reports the existing attachment

### Requirement: Treat Grill context as supplemental planning input

When applicable change-linked `grill.md` context exists, OpenSpec proposal, specification, design, and task work SHALL use its confirmed intent, constraints, decisions, resolved assumptions, non-goals, and open questions as supplemental planning input. The context SHALL remain separate from the stock OpenSpec schema artifact set.

#### Scenario: Proposal uses attached Grill context

- **WHEN** a user creates planning artifacts for a change with attached `grill.md`
- **THEN** the artifacts retain relevant confirmed decisions and non-goals, and the change still uses the stock OpenSpec artifact set

#### Scenario: No Grill context exists

- **WHEN** a change has no applicable `grill.md`
- **THEN** normal OpenSpec proposal, specification, design, and task work remains available without a forced Grill step

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
