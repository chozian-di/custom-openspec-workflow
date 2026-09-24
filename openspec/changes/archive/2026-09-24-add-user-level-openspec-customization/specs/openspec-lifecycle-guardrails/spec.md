# Spec Delta

## Purpose

This capability adds evidence and decision points to the normal OpenSpec lifecycle. It keeps the workflow lightweight for changes that do not need a given check and keeps implementation, planning, acceptance, verification, and archival decisions explicit. It preserves the boundary between planning artifacts and implementation work.

## ADDED Requirements

### Requirement: Keep lifecycle guidance advisory

Policy and operation guidance SHALL direct the agent and user without claiming hard enforcement. The guidance MUST NOT replace native OpenSpec commands or claim that a recommendation alone completed UAT, performed Verify, or made Archive safe. Native schema behavior, command behavior, task tracking, Archive checks, and explicit user decisions remain authoritative.

#### Scenario: Guidance gives a recommendation

- **WHEN** the customization gives an Apply, UAT, Verify, or Archive recommendation
- **THEN** the recommendation is presented as advisory guidance and does not claim that the guidance alone enforced the result

#### Scenario: Native OpenSpec remains authoritative

- **WHEN** a native OpenSpec command or explicit user decision conflicts with advisory guidance
- **THEN** the workflow preserves native command behavior and records the user decision instead of claiming that guidance overrode it

### Requirement: Preserve the normal lifecycle and the Apply versus Update boundary

The customized guidance SHALL support optional Grill, optional Explore, Propose, Apply, coherent implementation work, automated checks, required Human UAT when applicable, Verify, and Archive. When implementation exposes a planning problem, the guidance SHALL direct the user to Update and then Apply. It MUST NOT silently change planning intent during Apply.

#### Scenario: Simple change

- **WHEN** a trivial change has sufficient requirements without deeper interrogation
- **THEN** the workflow allows Propose and Apply without unnecessary Grill or UAT ceremony

#### Scenario: Implementation problem

- **WHEN** the proposal, specifications, and design correctly describe the desired behavior but the implementation does not satisfy them
- **THEN** the workflow directs the user to Apply

#### Scenario: Planning problem

- **WHEN** implementation shows that the plan is incomplete, incorrect, contradictory, or no longer represents the desired behavior
- **THEN** the workflow reports the issue, directs the user to Update, and returns to Apply after the planning decision

### Requirement: Generate coherent tasks and automated test work

The customized task guidance SHALL use stock `tasks.md`. It SHALL group related work coherently and can reflect useful dependency order. It MUST NOT add `verification.md`, a custom scheduler, fixed execution waves, or static worker, token, mutex, agent, or parallel-safety metadata. It MUST NOT describe task guidance as a scheduler or hard execution enforcement.

For changed behavior that is reasonably unit-testable, the guidance SHALL require suitable unit tests. Test-Driven Development is not required. Tests do not need to precede implementation. The guidance SHALL prefer project-native automated checks whenever they can reasonably establish behavior.

#### Scenario: Automated-only change

- **WHEN** a change can be established by automated checks and has no residual human acceptance criterion
- **THEN** the planned path is Propose, Apply, automated tests, no UAT needed, Verify, and Archive

#### Scenario: Unit testing does not require TDD

- **WHEN** changed behavior has a suitable unit test path
- **THEN** tasks require an appropriate unit test but allow implementation before the test and do not impose a RED, GREEN, REFACTOR process

#### Scenario: Manual work would duplicate automation

- **WHEN** a reliable automated check establishes an acceptance criterion
- **THEN** the task plan does not add a duplicate manual acceptance task

### Requirement: Require applicable Human UAT

Human UAT SHALL be required when a criterion cannot reasonably or adequately be established through automation, unless the user explicitly waives that specific criterion. Examples include subjective appearance, interaction quality, UX expectations, human interpretation, unavailable hardware or environments, and confirmation that behavior matches user intent when automation cannot establish that judgment.

Applicable UAT SHALL appear in `tasks.md` as normal task checkboxes. The guidance SHALL create separate tasks for independently invalidatable behaviors. Apply guidance MUST instruct the agent to pause at outstanding UAT and give clear manual steps and expected results.

When automation establishes every acceptance criterion, the workflow SHALL record why UAT does not apply with a durable note such as `HUMAN UAT - NOT APPLICABLE: covered by <automated evidence>`. This note is evidence that UAT was considered, not a pass or a waiver, and SHALL NOT create an unrelated manual task.

Only the user may authorize a UAT pass or waiver. The agent MUST NOT mark UAT passed from its own inspection, infer user acceptance, claim that manual acceptance occurred without the user, or waive UAT by itself. Explicit user disposition SHALL use distinguishable records such as `HUMAN UAT - PASSED` and `HUMAN UAT - WAIVED BY USER`.

#### Scenario: Human UAT is required

- **WHEN** a change has user-visible or integration behavior that automation does not fully cover
- **THEN** the task plan contains separate applicable UAT tasks, Apply waits for user disposition, and Verify follows completed Apply and UAT

#### Scenario: Human UAT does not apply

- **WHEN** the change has no user-visible or integration behavior that needs human acceptance
- **THEN** the workflow records a reason such as `HUMAN UAT - NOT APPLICABLE: covered by <automated evidence>` and does not force an unrelated manual test

#### Scenario: User passes a UAT scenario

- **WHEN** the user explicitly confirms a named UAT scenario
- **THEN** the corresponding task is completed with a durable `PASSED` record that does not claim more testing than the user confirmed

#### Scenario: User waives a UAT scenario

- **WHEN** the user explicitly chooses to waive a named applicable UAT scenario
- **THEN** the corresponding task is completed with `WAIVED BY USER`, remains distinguishable from `PASSED`, and does not rely on agent inference

#### Scenario: User requests Archive with UAT outstanding

- **WHEN** required UAT remains incomplete and the user requests Archive
- **THEN** the workflow names the scenarios and asks the user to perform each one or explicitly waive each one

### Requirement: Invalidate only affected UAT

A Verify finding alone MUST NOT invalidate completed UAT. After a substantive implementation change, the guidance SHALL assess each passed or waived UAT scenario and reset only scenarios that the change could reasonably affect.

A waiver SHALL apply only to the implementation state for which the user granted it. A later substantive change that affects the waived behavior SHALL reset that scenario to incomplete. Unrelated passed or waived scenarios SHALL remain resolved.

#### Scenario: Verify finds an issue without implementation change

- **WHEN** Verify reports a finding but no substantive implementation change has occurred
- **THEN** completed UAT remains valid until an implementation change affects a scenario

#### Scenario: Verify-driven implementation change

- **WHEN** a code or behavior change is made in response to a Verify finding
- **THEN** the previous Verify result is stale and only affected UAT scenarios are reopened

#### Scenario: Selective UAT invalidation

- **WHEN** several UAT scenarios are passed or waived and a later change affects only one
- **THEN** only the affected scenario becomes incomplete and unrelated scenarios retain their records

#### Scenario: Waiver invalidation

- **WHEN** a user waived a scenario and a later substantive change affects its covered behavior
- **THEN** the prior waiver is reset and the scenario requires new user disposition

### Requirement: Keep Apply context-conscious

Before implementation, Apply guidance SHALL direct the agent to read the current repository state, relevant configuration, tests, planning artifacts, and applicable supplemental `grill.md`. If current state conflicts with planning intent, the workflow SHALL report the conflict and pause for Update or another explicit user decision.

Apply SHALL work through coherent groups of related tasks. After a group it SHALL run focused automated checks, mark completed tasks, refresh current OpenSpec Apply state, reassess remaining work, and select the next group.

#### Scenario: Repository matches the plan

- **WHEN** Apply starts and current repository state agrees with the planning artifacts
- **THEN** the agent proceeds under the existing plan and selects a coherent work group

#### Scenario: Repository differs from the plan

- **WHEN** current repository state conflicts with a requirement or task
- **THEN** the workflow reports the conflict and pauses for Update or an explicit user decision before implementation continues

#### Scenario: Coherent group completes

- **WHEN** a coherent implementation group reaches its boundary
- **THEN** Apply runs focused automated checks, records completed tasks, refreshes persisted state, and reassesses the next group

### Requirement: Re-anchor from persisted OpenSpec state

The guidance SHALL define re-anchor as refreshing understanding from authoritative persisted OpenSpec state rather than relying indefinitely on earlier conversation. A lightweight re-anchor SHALL use the native fresh Apply instruction or state surface and refresh current progress, completed and remaining tasks, current Apply state, current operation guidance, and the next coherent work group. It MUST NOT reread all planning artifacts or the whole repository after every task without a reason.

A full re-anchor SHALL reread relevant planning artifacts and repository context after a meaningful interruption, planning artifact change, OpenSpec Update, material assumption or design problem, delegated work that affects later implementation, or a conflict between code and the recorded plan.

Delegation SHALL remain optional. The workflow can use reliable native subagent delegation for substantial independent coherent groups with focused context and non-conflicting edits. It MUST NOT require one worker per checkbox or mandatory subagents.

#### Scenario: Lightweight re-anchor

- **WHEN** a coherent group completes without a planning change or material conflict
- **THEN** Apply refreshes persisted task and operation state without rereading every planning artifact or the entire repository

#### Scenario: Full re-anchor

- **WHEN** work resumes after interruption or planning changes through Update
- **THEN** the agent rereads relevant planning artifacts and repository context before continuing

### Requirement: Verify the completed Apply work

The customized workflow SHALL enable the normal `/opsx:verify` capability. Verify SHALL be a workflow-level review, not a `tasks.md` checkbox. After all Apply tasks and applicable UAT are resolved, Apply guidance SHALL point to Verify before Archive. This order uses native incomplete-task protection for applicable UAT before the workflow-level Verify review.

Verify SHALL compare requirements, scenarios, tasks, automated test results, and applicable UAT results. It SHALL report unresolved gaps and SHALL not describe the change as clean while required evidence is incomplete.

#### Scenario: Verify follows Apply and UAT

- **WHEN** all implementation tasks and applicable UAT tasks are resolved
- **THEN** the next recommended workflow step is `/opsx:verify`, not immediate Archive

#### Scenario: Verification passes

- **WHEN** requirements, scenarios, tasks, automated tests, and applicable UAT results have no unresolved gaps
- **THEN** Verify reports the change as ready for Archive

#### Scenario: Verification finds a gap

- **WHEN** Verify finds an unmet requirement, incomplete task, failed test, or failed acceptance step
- **THEN** Verify reports the gap and directs the user to Apply or Update before Archive

#### Scenario: Verify becomes stale

- **WHEN** substantive implementation changes after a Verify result
- **THEN** the previous Verify result is invalidated and the workflow requires Apply, affected UAT when needed, and Verify again

#### Scenario: Verify remains valid after a non-substantive change

- **WHEN** a later change cannot affect implementation correctness
- **THEN** the prior Verify result can remain valid, but uncertainty leads the workflow to run Verify again

### Requirement: Protect the Archive decision

Before recommending or performing normal Archive, the guidance SHALL assess whether normal implementation tasks are resolved, required Human UAT is passed or explicitly waived by the user, no passed or waived UAT was invalidated by later relevant implementation, and Verify covers the most recent substantive implementation state.

If Verify is absent, stale, or uncertain, the guidance SHALL recommend Verify instead of Archive. If required UAT is incomplete, the guidance SHALL not recommend Archive by default. It can continue only after the user explicitly waives each named scenario, with `WAIVED BY USER` recorded. The guidance MUST retain normal OpenSpec incomplete-task protection and MUST preserve unresolved requirements, test evidence, Grill context, and project configuration.

#### Scenario: Clean change archives

- **WHEN** Verify reports no unresolved required work and the user confirms Archive
- **THEN** the normal OpenSpec Archive workflow can move the complete change while preserving its planning artifacts and evidence

#### Scenario: Verify is absent

- **WHEN** normal implementation tasks and UAT are complete but no current Verify evidence exists
- **THEN** the workflow recommends Verify and does not recommend Archive as the immediate next step

#### Scenario: Verify is stale

- **WHEN** a substantive implementation change occurred after the last Verify
- **THEN** the workflow reports stale Verify evidence and directs the user through affected UAT and Verify again

#### Scenario: Required UAT is incomplete

- **WHEN** one or more required UAT tasks remain incomplete
- **THEN** the workflow reports the named scenarios and requires user pass or explicit `WAIVED BY USER` disposition before treating Archive as ready
