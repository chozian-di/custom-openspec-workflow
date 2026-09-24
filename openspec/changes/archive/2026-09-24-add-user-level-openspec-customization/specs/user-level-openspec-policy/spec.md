# Spec Delta

## Purpose

This capability provides one reusable user-level OpenSpec customization package. It targets brownfield software development and adds policy and guidance across repositories while keeping OpenSpec's lightweight, fluid stock workflow and its upstream ownership. It minimizes maintenance burden and remains resilient to future OpenSpec and Grill Me upgrades.

## ADDED Requirements

### Requirement: Preserve the stock OpenSpec boundary

The package SHALL use the stock `spec-driven` schema and supported OpenSpec extension points, including `openspec/config.yaml`, per-artifact rules, `operations.apply.guidance`, `operations.archive.guidance`, user-level skills, and a thin bootstrap. It SHALL retain suitable stock behavior. It MUST NOT fork the schema, modify OpenSpec source, modify generated `openspec-*` skills, shadow official commands, or replace Apply, Verify, or Archive with custom implementations.

#### Scenario: User initializes a target repository

- **WHEN** the customization prepares a target repository
- **THEN** the repository remains a stock `spec-driven` OpenSpec project, its generated upstream files remain available, and the custom components remain separate

#### Scenario: A stock capability limitation is found

- **WHEN** a requirement cannot use stock `spec-driven`, supported project configuration, user-level skills, and a thin bootstrap
- **THEN** the limitation is recorded before implementation adds a schema fork, replacement command, or other prohibited component

### Requirement: Complete the pre-implementation capability callout

Before any implementation deliverable is created, the plan SHALL compare every target requirement with stock `spec-driven`, supported project configuration, user-level skills, and a thin bootstrap. The plan SHALL record evidence for each result. If a requirement cannot use those surfaces, implementation SHALL stop and surface the requirement and reason before introducing a custom schema, replacement command, custom lifecycle implementation, or other non-goal. A custom Apply implementation requires separate evidence that configuration guidance is insufficient.

#### Scenario: Stock capability feasibility is recorded

- **WHEN** implementation planning reaches the pre-implementation gate
- **THEN** the plan records whether each target requirement fits the stock schema, supported configuration, user-level skills, and thin bootstrap before implementation deliverables begin

#### Scenario: A target requirement exceeds the stock boundary

- **WHEN** the feasibility callout finds a requirement that the supported surfaces cannot achieve
- **THEN** the plan records the limitation and stops for a new decision before the implementation crosses a stated non-goal

### Requirement: Record the published OpenSpec baseline

The package SHALL determine the installed OpenSpec version and the current published release selected for the customization. It SHALL record the release used for design and testing. Upstream behavior inspection SHALL use the corresponding published release rather than arbitrary content from GitHub `main`.

#### Scenario: User checks compatibility

- **WHEN** a user reviews the package compatibility record
- **THEN** the record identifies the installed version, the selected published release, and the validation evidence for that release

#### Scenario: Upstream behavior is inspected

- **WHEN** implementation needs to inspect OpenSpec behavior
- **THEN** it uses the source for the recorded published release and does not use unreleased `main` content as the baseline

### Requirement: Provide a reusable user-level package

The package SHALL provide a canonical policy or configuration source, `custom-openspec-init`, `custom-openspec-grill`, only necessary support scripts, and a comprehensive `README.md`. A user MUST be able to use the package across repositories without copying policy files or skills into each repository.

#### Scenario: User installs the package

- **WHEN** a user installs the customization on the supported coding-agent host
- **THEN** the user can discover and use `custom-openspec-init` and `custom-openspec-grill` from user-level locations without copying them into each target repository

#### Scenario: The host has different user-level locations

- **WHEN** the supported host uses specific user-level skill or executable locations
- **THEN** installation discovers and reports those locations instead of assuming a layout used by another host

#### Scenario: The package uses custom skill names

- **WHEN** the package installs its custom skills
- **THEN** the Grill adapter uses the physical name `custom-openspec-grill` and does not use an OpenSpec-reserved or generated `openspec-*` name

### Requirement: Document the complete workflow

The package `README.md` SHALL explain what is upstream, what is custom, user-level installation, bootstrap, host considerations, the Grill Me prerequisite, new-project setup, optional Grill, Explore, Propose, Apply, Update, Verify, Archive, testing, UAT, the `HUMAN UAT - NOT APPLICABLE` record with its reason, re-anchoring, Git worktrees, upgrades, troubleshooting, quality, non-goals, the advisory nature of guidance, and the separation between planning artifacts and implementation deliverables. It SHALL include the lifecycle diagram and the desired outcome of a normal stock `spec-driven` project with additional user policy.

#### Scenario: User follows the README

- **WHEN** a user reads the package documentation before starting a change
- **THEN** the user can identify the next applicable lifecycle step, the distinction between Apply and Update, the evidence required before Archive, and the upstream or custom owner of each component

#### Scenario: User reads the lifecycle diagram

- **WHEN** a user reviews the documented lifecycle
- **THEN** the diagram shows optional Grill, optional Explore, Propose, Apply, automated tests, re-anchoring, applicable UAT, Verify, Update loops, and Archive

### Requirement: Keep customization guidance advisory

Policy and operation guidance SHALL direct the agent and user without claiming hard enforcement. The package MUST NOT present guidance as a replacement for native OpenSpec commands or as proof that UAT, Verify, or Archive occurred. Native schema behavior, command behavior, task tracking, Archive checks, and explicit user decisions remain authoritative.

#### Scenario: User reads a guidance recommendation

- **WHEN** the package gives an Apply, Verify, UAT, or Archive recommendation
- **THEN** the documentation identifies it as guidance and does not claim that the recommendation alone enforced the result

### Requirement: Document upgrade and maintenance behavior

The package SHALL document the normal OpenSpec upgrade path, including the desired published release, normal `openspec update`, review of configuration, skills, and workflows, supported-surface checks, and customization smoke tests. It SHALL document independent Grill Me upgrades and a compatibility test that discovers the installed dependency, reports stage and attachment evidence, and does not depend on exact prompt wording, line positions, or filename slug rules.

#### Scenario: User upgrades OpenSpec

- **WHEN** a user upgrades OpenSpec
- **THEN** the user can run the normal update path, review the supported surfaces, and run the customization smoke tests without merging a vendored schema fork

#### Scenario: User upgrades Grill Me

- **WHEN** the upstream Grill Me skill changes
- **THEN** the user can test dependency discovery, delegation, supplemental context, staging, attachment, repeated attachment, traceability, optional use, and no implementation behavior while leaving Grill Me unchanged

### Requirement: Document Git and source isolation

The README SHALL state that OpenSpec change folders isolate planning artifacts but do not isolate source-code changes. It SHALL recommend Git branches or worktrees for multiple partially implemented independent changes and SHALL leave branch, worktree, commit, merge, rebase, and source conflict operations to Git.

#### Scenario: User works on concurrent changes

- **WHEN** two independent changes have partial source modifications
- **THEN** the documentation directs the user to Git branch or worktree isolation and does not imply that OpenSpec change folders provide source isolation

### Requirement: Meet the package quality boundary

The customization SHALL be small, understandable, version-controlled, idempotent where applicable, easy to remove, easy to inspect, explicit about changes, conservative with existing project configuration, and minimally coupled to OpenSpec and Grill Me internals. It MUST NOT implement a custom schema, `verification.md`, custom Apply, Verify, or Archive implementations, a replacement lifecycle, a task scheduler, fixed execution waves, static parallel-safe task annotations, mandatory subagents, TDD enforcement, automatic Git isolation, automatic UAT waiver, or upstream modifications.

#### Scenario: User inspects the package

- **WHEN** a user reviews the package contents and documented behavior
- **THEN** the package exposes its changes and dependencies clearly and contains no prohibited replacement framework

#### Scenario: A non-goal appears necessary

- **WHEN** implementation appears to require a stated non-goal
- **THEN** implementation stops and surfaces the requirement and reason before the boundary changes
