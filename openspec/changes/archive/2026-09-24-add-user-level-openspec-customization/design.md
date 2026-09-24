# Design

## Context

This change adds a user-level package that augments the stock OpenSpec `spec-driven` workflow. The package targets brownfield software development. It preserves OpenSpec's lightweight, fluid workflow while adding requirements discovery, testing expectations, human acceptance checks, context-conscious Apply guidance, Verify expectations, and Archive safety.

The design minimizes maintenance burden and remains resilient to future OpenSpec and Grill Me upgrades.

The package is an add-on. The upstream OpenSpec executable, schema, generated skills, and official commands remain authoritative. The upstream Grill Me skill remains the requirements-questioning dependency.

## Constraints and release baseline

The design uses these supported OpenSpec surfaces:

- `openspec/config.yaml`.
- Per-artifact rules.
- `operations.apply.guidance`.
- `operations.archive.guidance`.
- User-level or custom skills.
- A small bootstrap mechanism.

The design does not fork `spec-driven`, modify OpenSpec source, modify generated `openspec-*` skills, shadow official commands, or add replacement Apply, Verify, or Archive implementations.

Before implementation begins, inspect the installed OpenSpec version and select the current published release used as the compatibility baseline. Record that release in the package documentation and validation evidence. When upstream behavior needs inspection, use the source for that published release. Do not use arbitrary GitHub `main` content as the source of truth.

The implementation must identify the supported coding-agent host before it chooses user-level skill and executable locations. It must discover those locations rather than assume that every host uses the same directories.

The adapter depends on the upstream Grill Me skill from `satya-janghu/agent-skills`. The adapter must use a small public behavior contract and must not copy or modify Grill Me interrogation logic.

Before implementation begins, the plan must complete a feasibility callout for every target requirement. The callout compares stock `spec-driven`, supported project configuration, user-level skills, and a thin bootstrap. It records evidence for requirements that fit those surfaces. If a requirement does not fit, implementation stops and surfaces the limitation before adding a custom schema, replacement command, custom lifecycle implementation, or other non-goal. A custom Apply implementation requires separate evidence that configuration guidance is insufficient.

## Architecture

The boundary between upstream and custom components is:

```text
upstream OpenSpec
  stock spec-driven schema
  official executable and commands
  generated openspec-* skills
          |
          v
supported configuration and guidance
  openspec/config.yaml
  artifact rules
  Apply guidance
  Archive guidance
          |
          v
user-level customization package
  canonical policy source
  custom-openspec-init
  custom-openspec-grill
  necessary support scripts
  README.md
          |
          v
target repository
  normal OpenSpec files
  stock generated skills
  merged policy
  change-local supplemental grill.md
```

The package changes policy and guidance through supported surfaces. It does not create a framework inside OpenSpec.

The proposal, design, specifications, and `tasks.md` are planning artifacts. The canonical policy source, bootstrap, Grill adapter, necessary support scripts, tests and fixtures, and `README.md` are implementation deliverables. Change-local `grill.md` is supplemental planning context, not a schema artifact. Verify is a workflow review, not a task or package deliverable.

## Components and decisions

### Canonical package source

The package contains one canonical policy or configuration source. It contains the reusable per-artifact rules and Apply and Archive guidance. It does not replace project context. Project context and project-specific rules remain owned by each target repository.

The package also contains `custom-openspec-init`, `custom-openspec-grill`, only support scripts that the workflow needs, and a comprehensive `README.md`. The physical name `custom-openspec-grill` does not use an OpenSpec-reserved or generated `openspec-*` skill name.

The installer places the package in user-level locations discovered from the supported host. It reports the locations it uses and reports an unsupported host without guessing a different host layout. The design does not invent a fixed host path.

### OpenSpec release discovery

The first implementation step is a compatibility check. It records:

1. The installed OpenSpec version.
2. The current published release selected as the package baseline.
3. The supported configuration and workflow surfaces used by the package.
4. The validation evidence for that release.

If the installed version and selected published release differ, the implementation records the distinction and resolves it before relying on release-specific behavior. The package does not copy behavior from an arbitrary unreleased source or invent a fixed Grill Me revision when the installed dependency must be discovered.

### Bootstrap for new repositories

`custom-openspec-init` first uses normal `openspec init` behavior when a repository has no OpenSpec root. It preserves the files that normal OpenSpec generates. It keeps the project on stock `spec-driven`.

The helper then applies the canonical policy through supported configuration. It enables the supported OpenSpec workflow or profile required for `/opsx:verify`. It reports the resulting changes.

### Bootstrap for existing repositories

When a repository already has OpenSpec files, the helper performs a read-only preflight and augments the repository in place. It does not destructively reinitialize the project. It preserves:

- Existing generated OpenSpec files.
- Project context.
- Project-specific rules.
- Existing project-specific configuration.
- User-owned files.

The helper retains project-specific configuration as a valid later extension point. If the target uses a non-stock schema, the helper reports that the stock boundary does not apply and does not silently replace the schema.

### Policy merge and idempotence

The helper merges policy entries into `openspec/config.yaml`. The merge preserves existing project-owned values and adds only missing package entries. Repeated runs avoid creating duplicate package entries. The helper reports pre-existing duplicate project entries instead of silently deleting user-owned configuration. A second run produces the same effective configuration and reports no unnecessary changes.

The helper validates the resulting OpenSpec configuration where the selected release supports validation. If the target configuration cannot be read, the policy cannot be merged safely, Verify enablement cannot be applied, or validation fails, the helper restores files changed by the customization to their pre-run state. It leaves unrelated user changes untouched, reports the failure and rollback, and does not write a partial result.

The implementation must make overwrite behavior conservative. It must report changed files and changed configuration entries. It must not replace the `openspec` executable or disguise the helper as upstream OpenSpec.

### Verify workflow availability

The helper uses the normal supported profile or workflow configuration to make `/opsx:verify` available. It preserves existing workflow choices and adds only the missing Verify capability. It does not replace the generated Verify skill and does not create a custom Verify implementation.

The README documents the observed supported configuration surface and the validation step that confirms Verify availability.

### Thin Grill adapter

`custom-openspec-grill` delegates the question loop to the installed upstream Grill Me skill. The adapter does not reproduce its interrogation process. It consumes the distilled result and creates OpenSpec-oriented supplemental context.

The adapter preserves these sections in `grill.md`:

- Intent.
- Constraints.
- Decisions.
- Assumptions Surfaced.
- Open Questions.
- Non-Goals or Out of Scope.

The adapter distinguishes resolved decisions from unresolved questions. It performs no implementation work. It is useful for ambiguous, substantial, architectural, UX-sensitive, security-sensitive, or otherwise underspecified work. It does not force Grill for trivial or already-specified work.

### Grill staging before a change exists

Grill can run before an OpenSpec change exists. The adapter uses the least invasive non-root staging path available for the upstream Grill result. The normal upstream `.grill/<slug>.md` result can remain source material. Any package-owned staging metadata must also remain outside the repository root.

The adapter records enough source identity to connect one session to a later named change. The association must not depend only on the Grill filename slug. The design uses a stable session identifier or an equivalent durable identity. The exact identifier format is an implementation detail and must be documented with the staging procedure.

Before a change exists, the adapter does not create root-level `grill.md`, a custom schema artifact, or an unrelated OpenSpec artifact. It reports the source identity so the user can attach the session later.

### Grill attachment after a change exists

After a named OpenSpec change exists, the adapter imports or distills the selected staged session into a `grill.md` file in that change. The file identifies the source session and preserves traceability to the source material. If a change-local context file already exists, the adapter preserves it and requests an explicit user decision before replacement or combination.

`grill.md` is supplemental context. It is not a first-class schema artifact. The adapter does not add it to the OpenSpec artifact graph and does not edit schema metadata to add it.

### Grill compatibility evidence

The compatibility command is an evidence-producing smoke test. It discovers the installed `grill-me` skill through the supported host location and reports dependency availability instead of using a literal delegation label. It uses disposable state to stage a representative result, attach it to a temporary named change, repeat the attachment, and inspect the resulting required sections, source identity, source hash, and supplemental status. It also checks that the optional-use path remains available and that the adapter performs no implementation work. Missing dependency or contract evidence produces an actionable failure and leaves the target repository, staged source, and upstream skill unchanged.

### Planning consumption of Grill context

When change-local `grill.md` exists, proposal, specification, design, and task generation read it as supplemental planning input. They retain confirmed intent, constraints, decisions, resolved assumptions, non-goals, and open questions. They do not silently discard those decisions.

The same context is available to Apply and Archive guidance when it helps resolve current intent or preserve planning evidence. The stock OpenSpec instructions remain controlling.

## Lifecycle decisions

The documented lifecycle is:

```text
Idea or problem
      |
      v
custom-openspec-grill, optional
      |
      v
grill.md, supplemental context
      |
      v
/opsx:explore, optional
      |
      v
/opsx:propose
      |
      v
/opsx:apply
      |
      +--> coherent implementation group
      |        |
      |        +--> focused automated checks
      |        +--> lightweight re-anchor
      |        +--> required Human UAT when applicable
      |
      +--> planning problem, /opsx:update, then /opsx:apply
      |
      v
/opsx:verify
      |
      +--> issue found, Apply or Update, affected UAT when invalidated,
           then Verify again
      |
      v
/opsx:archive
```

Apply is for an implementation problem against a correct plan. Update is for a plan that is incomplete, incorrect, contradictory, or changed. The normal loop is Apply, planning issue, Update, then Apply. The agent does not silently edit planning intent during Apply.

Policy and operation guidance are advisory instructions. They direct the agent and user, but they do not hard-enforce behavior or replace native OpenSpec commands. Native schema behavior, command behavior, task tracking, Archive checks, and explicit user decisions remain authoritative. The package must not claim that guidance alone completed UAT, performed Verify, or made Archive safe without the required native or user evidence.

## Task and testing decisions

The package extends stock `tasks.md`. It does not add `verification.md`, a scheduler, fixed execution waves, or static worker metadata. These rules are task-generation guidance, not a custom scheduler or hard execution enforcement.

Tasks are grouped by coherent implementation area. They can follow dependency order. They remain small enough to implement and check. A task list does not include worker assignments, scheduler waves, agent IDs, token estimates, mutex data, or parallel-safety labels.

When changed behavior is reasonably unit-testable, the task list includes suitable unit tests. Test-Driven Development is not required. The implementation can come before the tests. The task list prefers project-native automated checks, including integration, functional, API, UI, browser, static, lint, compilation, build, and other reliable checks.

Manual acceptance is residual only. The workflow does not create a manual task that duplicates a reliable automated check.

### Human UAT task representation

Applicable UAT appears as normal incomplete task checkboxes in `tasks.md`. Each independently invalidatable behavior has its own task. Apply guidance instructs the agent to pause when an applicable UAT task remains incomplete and to give the user manual steps and expected results.

When automation establishes every acceptance criterion, the task or acceptance record uses `HUMAN UAT - NOT APPLICABLE: <reason>` to show why no manual check is needed. This record is not a pass or waiver and does not become a checkbox requiring user disposition.

Only the user can authorize a UAT pass or waiver. The agent cannot mark UAT passed from its own inspection. It cannot infer user acceptance or a waiver. After explicit user approval, the task can use a durable form such as:

```text
[x] HUMAN UAT - PASSED: Confirm the modal interaction.
```

After explicit user waiver, the task can use:

```text
[x] HUMAN UAT - WAIVED BY USER: Confirm the modal interaction.
```

The waiver record is not a pass record. If the user requests Archive while required UAT remains incomplete, the workflow names each scenario and asks for the user to perform it or explicitly waive it.

### Selective UAT invalidation

A Verify finding alone does not invalidate completed UAT. A later substantive implementation change requires an impact review against each passed or waived UAT scenario. Only scenarios that could reasonably be affected are reset to incomplete. Unrelated scenarios remain resolved.

A waiver applies only to the implementation state for which it was granted. A later substantive change that affects the waived behavior resets that waiver. The workflow never carries the waiver forward silently.

## Apply guidance and re-anchoring

Apply reads the current repository state, relevant configuration, tests, and planning artifacts before implementation. If repository reality conflicts with planning intent, Apply reports the conflict and pauses for Update or another explicit user decision.

Apply works through coherent groups of related tasks. At each group boundary it runs focused automated checks, marks completed tasks promptly, refreshes current OpenSpec Apply state, reassesses remaining work, and selects the next group.

Re-anchor means refreshing understanding from the authoritative persisted OpenSpec state rather than relying indefinitely on earlier conversation. A lightweight re-anchor uses the native fresh Apply instruction or state surface and refreshes:

- Current progress.
- Completed and remaining tasks.
- Current Apply state.
- Current operation guidance.
- The next coherent work group.

The lightweight operation does not reread every planning artifact or the entire repository after every task.

A full re-anchor rereads relevant planning artifacts and current repository context after a meaningful interruption, an OpenSpec Update, any planning artifact change, a material assumption or design problem, delegated work that affects later implementation, or a conflict between code and the recorded plan.

Delegation is optional. Native subagent delegation can be used only when the host supports it reliably and when independent coherent groups, focused context, and non-conflicting edits make delegation useful. The package does not require subagents.

## Verify policy

Verify is a workflow-level review. It is not a `tasks.md` checkbox.

The normal order is Apply, required or waived UAT, Verify, then Archive. This order uses native incomplete-task protection for applicable UAT before the workflow-level Verify review. After all Apply tasks and applicable UAT are resolved, Apply guidance points to `/opsx:verify` instead of recommending Archive immediately.

Verify compares the requirements, scenarios, tasks, automated test results, and applicable UAT results. It reports unresolved gaps and does not call the change clean while required evidence is incomplete.

A Verify result applies only to the substantive implementation state it inspected. Any later substantive implementation change makes the result stale. The next path is Apply, affected UAT when invalidated, then Verify again. A non-substantive change that cannot affect implementation correctness can retain the result, but uncertainty favors running Verify again. A Verify finding without an implementation change does not invalidate UAT.

## Archive policy

Before Archive guidance recommends or performs the normal archive, it assesses:

1. Normal implementation tasks are resolved.
2. Required Human UAT scenarios are passed or explicitly waived by the user.
3. No passed or waived UAT scenario was affected by later implementation.
4. Verify covers the most recent substantive implementation state.

If Verify is absent, stale, or uncertain, guidance recommends Verify. If required UAT is incomplete, guidance does not recommend Archive by default. It names the remaining scenarios and allows continuation only after explicit user waivers are recorded as `WAIVED BY USER`.

The guidance retains normal OpenSpec incomplete-task protection. A user can choose an exception, but the exception is explicit and auditable.

## Git and worktree isolation

OpenSpec change folders isolate planning artifacts. They do not isolate source code. Multiple changes can be explored or planned concurrently. Multiple independent changes with partial source modifications do not normally share one working tree.

The README recommends a Git branch or worktree when work pauses for another change, an urgent fix is needed, or independent implementations proceed concurrently. Git remains responsible for branches, worktrees, commits, merges, rebases, and source conflict resolution. The package does not create or manage them automatically.

## Upgrade strategy

For OpenSpec:

1. Upgrade to the desired published release.
2. Run normal `openspec update`.
3. Review configuration, skill, and workflow changes.
4. Confirm that the supported package surfaces remain valid.
5. Run the customization smoke tests.

The package has no vendored `spec-driven` schema diff or merge process because it does not fork the schema. A future schema fork requires a new explicit decision.

For Grill Me, keep the upstream skill unchanged and independently upgradeable. The adapter depends on the smallest practical public output contract. It does not rely on exact prompts, line numbers, prose, or filename slug rules. It extracts required meaning semantically where the output structure allows it. After an upstream update, the compatibility test reports dependency discovery and checks delegation, required `grill.md` sections, source traceability, pre-change staging, change attachment, repeated attachment, optional use, and no implementation behavior in isolated state.

## README design

The README is thorough but practical. It explains:

- What the customization adds.
- Why stock `spec-driven` remains in use.
- What remains upstream and what is custom.
- User-level installation and host-specific discovery.
- Bootstrap for new and initialized repositories.
- Grill prerequisites, optional use, Explore relationship, and `grill.md`.
- The complete lifecycle diagram.
- Apply versus Update.
- Unit tests, no TDD requirement, automated verification, and residual UAT.
- UAT pass, waiver, a reasoned `NOT APPLICABLE` record, selective invalidation, and waiver invalidation.
- Verify ordering, scope, and freshness.
- The advisory nature of policy and operation guidance and the limits of hard enforcement.
- Lightweight and full re-anchoring.
- The separation between planning artifacts and implementation deliverables.
- Git branches and worktrees.
- OpenSpec and Grill Me upgrades.
- Troubleshooting for skipped Verify, stale Verify, incomplete UAT, Archive with UAT outstanding, planning flaws, missing Grill output, and repeated bootstrap.

## Quality and non-goals

The package is small, understandable, version-controlled, idempotent where applicable, easy to remove, easy to inspect, explicit about changes, conservative about existing configuration, and minimally coupled to OpenSpec and Grill Me internals. It prefers simple scripts and configuration over orchestration.

The initial implementation excludes:

- A custom OpenSpec schema.
- `verification.md`.
- A custom Apply skill.
- A custom Verify skill.
- A custom Archive implementation.
- A replacement lifecycle implementation.
- A task scheduler.
- CP-SAT scheduling.
- Fixed execution waves.
- Static parallel-safe task annotations.
- Mandatory subagents.
- TDD enforcement.
- Automatic Git branch or worktree manipulation.
- Automatic UAT waiver.
- Changes to upstream Grill Me.
- Changes to upstream OpenSpec-generated skills.

If a requirement cannot use stock `spec-driven`, supported project configuration, user-level skills, and a thin bootstrap, the implementation must stop before adding one of these exclusions. The reason and the affected requirement must be surfaced for a new decision.

## Validation approach

Use a disposable brownfield-style repository. The validation suite first records the pre-implementation feasibility callout and covers rollback evidence for invalid setup. It then covers:

1. Simple change, with no unnecessary Grill or UAT ceremony.
2. Automated-only change, with Propose, Apply, automated tests, a recorded `HUMAN UAT - NOT APPLICABLE` reason, Verify, and Archive.
3. Human UAT required, with independent tasks, an Apply pause, no agent self-pass, and Verify after UAT.
4. Explicit UAT waiver, with a distinct `WAIVED BY USER` record and valid Archive preparation.
5. UAT failure, with correct Apply versus Update classification.
6. Verify finding, with no UAT invalidation from the finding alone and stale Verify after substantive code change.
7. Selective UAT invalidation, with only affected scenarios reopened.
8. Waiver invalidation after substantive change to the waived behavior.
9. Lightweight and full re-anchoring at the defined lifecycle points.
10. Premature Archive with missing Verify, stale Verify, or incomplete required UAT.
11. Repeated bootstrap with no duplicate rules, preserved context, and preserved stock files.
12. OpenSpec and Grill Me upgrade smoke testing, including dependency discovery and isolated stage, attachment, repeated-attachment, traceability, and no-implementation evidence.
