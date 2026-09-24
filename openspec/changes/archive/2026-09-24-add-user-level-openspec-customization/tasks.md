# Tasks

These are planning tasks for one change. The proposal, design, specifications, and this `tasks.md` file are planning artifacts. The canonical policy source, bootstrap, Grill adapter, necessary support scripts, tests and fixtures, and `README.md` are implementation deliverables. Change-local `grill.md` remains supplemental planning context, and Verify remains a workflow review rather than a task.

## 1. Confirm the upstream boundary and baseline

- [x] 1.1 Inspect the installed OpenSpec version and select the current published release used as the compatibility baseline. Record the release used for design, implementation, and validation.
- [x] 1.2 Inspect the selected published release for the stock `spec-driven` schema, configuration fields, artifact rules, operation guidance, workflow or profile support, and user-level skill extension points. Do not use arbitrary GitHub `main` content as the baseline.
- [x] 1.3 Complete the mandatory pre-implementation feasibility callout. Compare every target requirement with stock `spec-driven`, supported project configuration, user-level skills, and a thin bootstrap. Record evidence for each result. Stop and surface the reason before introducing a custom schema, replacement command, custom lifecycle implementation, or other stated non-goal. Require separate evidence that configuration guidance is insufficient before considering a custom Apply implementation.
- [x] 1.4 Record the upstream Grill Me dependency from `satya-janghu/agent-skills` and define the smallest public behavior contract that the adapter needs. Confirm that the adapter will not modify or copy Grill Me interrogation logic.

## 2. Create the user-level package and documentation

- [x] 2.1 Create the package metadata, canonical policy or configuration source, `custom-openspec-init`, `custom-openspec-grill`, only necessary support scripts, tests, and fixtures. Keep custom components visibly separate from upstream components.
- [x] 2.2 Determine the supported coding-agent host and discover its user-level skill and executable locations. Install the custom skill and helper at the discovered locations. Report an unsupported host without guessing another host layout.
- [x] 2.3 Write the practical `README.md`. Cover the upstream boundary, release baseline, installation, bootstrap, new repositories, existing repositories, Grill and Explore, `grill.md`, the full lifecycle diagram, Apply versus Update, task and test policy, non-TDD testing, UAT, Verify, re-anchoring, Git worktrees, OpenSpec and Grill Me upgrades, troubleshooting, quality, and non-goals.

## 3. Add the policy and bootstrap behavior

- [x] 3.1 Add the canonical policy source with per-artifact rules and `operations.apply.guidance` and `operations.archive.guidance`. Use only supported configuration surfaces from the selected OpenSpec release. Do not add `verification.md` or a custom schema artifact.
- [x] 3.2 Implement the configuration merge for `openspec/config.yaml`. Preserve project context, project-specific rules, user-owned files, and other existing configuration. Add missing package entries and avoid exact duplicates.
- [x] 3.3 Implement fresh repository setup through normal `openspec init` behavior. Preserve generated OpenSpec files, retain stock `spec-driven`, apply the package policy, and enable the supported workflow or profile needed for `/opsx:verify`.
- [x] 3.4 Implement additive setup for an initialized repository. Use a safe preflight, preserve existing project content, and reject or report a non-stock schema instead of replacing it.
- [x] 3.5 Add result validation where the selected OpenSpec release supports it. Report changed files and configuration entries. Apply customization changes as one safe operation. If preflight, merge, Verify enablement, or validation fails, restore files changed by the customization to their pre-run state, leave unrelated user changes untouched, report the rollback, and do not write a partial result.
- [x] 3.6 Test repeated bootstrap runs. Confirm that effective configuration remains stable, package entries are not duplicated, generated files are not incorrectly overwritten, and project-specific configuration remains possible.

## 4. Add the thin Grill adapter and traceable staging

- [x] 4.1 Add the user-level skill named `custom-openspec-grill`. Make it delegate the question process to the installed upstream Grill Me skill. Confirm that it contains no copied interrogation logic and performs no implementation work.
- [x] 4.2 Support optional Grill use. Confirm that trivial or already-specified changes can use normal Explore or Propose without a Grill session.
- [x] 4.3 Implement pre-change staging in a non-root location. Retain the upstream Grill source material where possible, record a stable source identity, and avoid an unrelated root-level `grill.md` and any custom schema artifact.
- [x] 4.4 Implement attachment to a named OpenSpec change. Produce change-local `grill.md` or an equally unambiguous equivalent. Preserve the source identity and required sections, and do not rely only on a fragile filename slug.
- [x] 4.5 Preserve Intent, Constraints, Decisions, Assumptions Surfaced, Open Questions, and Non-Goals or Out of Scope. Distinguish resolved decisions from unresolved questions and preserve existing context unless the user chooses how to combine or replace it.
- [x] 4.6 Add planning input rules for proposal, specification, design, and task work. Confirm that applicable `grill.md` context is supplemental and does not become a schema artifact.

## 5. Add lifecycle, task, test, UAT, and Archive guardrails

- [x] 5.1 Add artifact rules that keep proposal, specification, design, and task work aligned with current repository context and attached Grill decisions.
- [x] 5.2 Add advisory Apply guidance for coherent task groups, focused automated checks, prompt task completion, current-state refresh, drift reporting, and the distinction between Apply and Update. Do not describe guidance as hard enforcement or as a replacement command.
- [x] 5.3 Add lightweight re-anchor guidance that refreshes persisted Apply state at coherent group boundaries. Add full re-anchor guidance for interruption, planning changes, Update, material assumptions, delegated work, and plan or repository conflicts.
- [x] 5.4 Add task-generation guidance for coherent grouping, dependency order where useful, stock `tasks.md`, automated verification, appropriate unit tests, and no TDD requirement. Confirm that implementation-first followed by tests remains valid and that manual work does not duplicate reliable automation.
- [x] 5.5 Add applicable Human UAT as independent normal task checkboxes. Require user disposition. Support explicit `PASSED` and `WAIVED BY USER` records. Prevent agent self-acceptance and automatic waiver. Add selective invalidation for later substantive changes, including waiver invalidation.
- [x] 5.6 Add advisory Verify guidance for the order Apply, required or waived UAT, Verify, Archive. Keep Verify out of `tasks.md`, compare requirements through acceptance evidence, and invalidate stale Verify after later substantive implementation changes. Include the rule that a non-substantive change can retain Verify only when it cannot affect correctness, with a rerun when uncertain.
- [x] 5.7 Add advisory Archive guidance that checks implementation tasks, UAT status, UAT invalidation, and fresh Verify evidence. Recommend Verify instead of Archive when evidence is missing, stale, or uncertain. Name incomplete UAT and require explicit user waivers before an exception. Do not claim that guidance alone hard-enforces the native Archive command.
- [x] 5.8 Document that OpenSpec change folders do not isolate source code. Add Git branch and worktree guidance without automatic branch or worktree manipulation.
- [x] 5.9 Document the normal OpenSpec upgrade and `openspec update` path. Document the independent Grill Me upgrade and compatibility test path. Keep the package easy to inspect, remove, and maintain.

## 6. Validate the customization

- [x] 6.1 Build a disposable brownfield-style repository matrix. Include the feasibility callout, fresh setup, initialized setup, repeated setup, invalid configuration with rollback, non-stock schema, missing Verify capability, pre-change Grill staging, post-change Grill attachment, lifecycle evidence, and Archive preparation.
- [x] 6.2 Validate Scenario 1, Simple change. Confirm that a trivial change receives no unnecessary Grill or UAT ceremony.
- [x] 6.3 Validate Scenario 2, Automated-only change. Confirm the path is Propose, Apply, automated tests, no UAT needed, Verify, then Archive.
- [x] 6.4 Validate Scenario 3, Human UAT required. Confirm that independent UAT tasks are generated, Apply pauses for user input, the agent cannot self-pass them, and Verify follows completed Apply and UAT.
- [x] 6.5 Validate Scenario 4, Explicit UAT waiver. Confirm that the user can waive a specific scenario, the record says `WAIVED BY USER`, it is distinct from `PASSED`, and Archive can proceed after the other checks.
- [x] 6.6 Validate Scenario 5, UAT failure. Confirm that an implementation problem goes to Apply and a planning or expectation problem goes to Update, then Apply.
- [x] 6.7 Validate Scenario 6, Verify discovers an issue. Confirm that a Verify finding alone does not invalidate UAT, that a substantive code change invalidates the previous Verify, and that only affected UAT scenarios reopen.
- [x] 6.8 Validate Scenario 7, Selective UAT invalidation. With several passed or waived scenarios, change behavior affecting only one scenario and confirm that only that scenario becomes incomplete.
- [x] 6.9 Validate Scenario 8, Waiver invalidation. Waive a scenario, materially change its covered behavior, and confirm that the prior waiver does not carry forward silently.
- [x] 6.10 Validate Scenario 9, Re-anchoring. Confirm lightweight re-anchoring at coherent group boundaries, full re-anchoring after meaningful interruption or Update, and no unnecessary reread of all planning artifacts after every task.
- [x] 6.11 Validate Scenario 10, Premature Archive. Attempt Archive without Verify, with stale Verify, and with required UAT outstanding. Confirm that guidance directs the user to the missing action and does not silently bypass it.
- [x] 6.12 Validate Scenario 11, Bootstrap idempotence. Run the bootstrap multiple times and confirm that policy is not duplicated, project context is preserved, and stock OpenSpec files are not incorrectly overwritten.
- [x] 6.13 Validate Scenario 12, Upgrade smoke test. Run the documented compatibility checks after an OpenSpec upgrade and after a Grill Me upgrade. Confirm that the selected published baseline, supported configuration surfaces, delegation, required `grill.md` sections, and traceability remain valid.
- [x] 6.14 Run the selected OpenSpec validation and status checks for the package fixtures and this change. Confirm that the artifacts remain valid, task checkboxes remain trackable, guidance remains advisory, no generated `openspec-*` skill changed, and no OpenSpec source changed.

## 7. Address verification findings

- [x] 7.1 Extend the Grill compatibility check to discover the installed `grill-me` dependency, exercise isolated staging, attachment, and repeated-attachment behavior, report actual traceability and no-implementation evidence, and leave target and upstream files unchanged; verify with focused adapter and validation-matrix tests.
- [x] 7.2 Update the canonical policy, README, UAT fixture, and contract tests to require `HUMAN UAT - NOT APPLICABLE: <reason>` when automation covers every acceptance criterion; verify the record is distinct from `PASSED` and `WAIVED BY USER` and does not create a manual task.
- [x] 7.3 Run the full package test command, the documented compatibility smoke test with its dependency result, and `openspec validate --all --json --no-interactive`; verify the updated artifacts and implementation remain coherent before running Verify again.
