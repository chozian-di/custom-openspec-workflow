# Custom OpenSpec workflow

This package adds a user-level policy to stock OpenSpec. It targets brownfield
software work in an existing repository.

OpenSpec remains the owner of the schema, commands, generated skills, task
tracking, and Archive behavior. This package adds policy, a bootstrap helper,
and a thin adapter for the upstream Grill Me skill.

The result is a normal OpenSpec project that uses the stock `spec-driven`
schema. The package does not create a new framework.

## What belongs to each project

OpenSpec owns these parts:

- The `spec-driven` schema.
- The `openspec` executable.
- Generated `openspec-*` skills.
- Explore, Propose, Apply, Update, Verify, and Archive commands.
- Artifact and task validation.

This package owns these parts:

- The policy in `src/custom_openspec_workflow/data/openspec-policy.yaml`.
- `custom-openspec-init`.
- `custom-openspec-grill` staging and attachment commands.
- The user-level `custom-openspec-grill` skill.
- Tests, fixtures, compatibility records, and this README.

The upstream Grill Me skill owns its question process. This package does not
copy or modify that skill.

## Compatibility baseline

This package uses the published `@fission-ai/openspec` release `1.13.2` as its
initial baseline. The installed executable and the published `latest` tag both
report `1.13.2` on the baseline date.

The evidence record is in
[`docs/compatibility-baseline.md`](docs/compatibility-baseline.md). It records
the inspected schema, configuration fields, profiles, Verify support, host
location, and Grill Me contract.

The package uses these OpenSpec configuration fields:

- `schema`.
- `context`.
- `rules`.
- `operations.apply.guidance`.
- `operations.archive.guidance`.

The package uses the supported global profile and workflow fields to expose
the native Verify skill. It does not add a `verification.md` file.

## Install for Codex

The supported host for this version is Codex. Codex reads user-level skills
from the shared `.agents/skills` directory.

From this repository, run:

```text
./scripts/custom-openspec-install \
  --host codex \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin
```

The installer places these files in user-level locations:

- `~/.agents/skills/custom-openspec-grill/SKILL.md`.
- `~/.local/bin/custom-openspec-init`.
- `~/.local/bin/custom-openspec-grill`.
- `~/.local/share/custom-openspec-workflow/custom_openspec_workflow`.

The installer does not install a different host layout. If the host is not
Codex, the installer reports that the host is unsupported. If the required
directories are not present or writable, pass explicit existing paths with
`--skills-dir` and `--bin-dir`.

You can set the host configuration with these variables:

```text
CUSTOM_OPENSPEC_WORKFLOW_HOST=codex
CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR=~/.agents/skills
CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR=~/.local/bin
```

Use `--install-dir` when you need a different package data root. The default
is `~/.local/share/custom-openspec-workflow`.

The upstream Grill Me skill is a prerequisite for Grill sessions. Install it
from `satya-janghu/agent-skills` with the host method that you use. The package
does not install or change Grill Me.

After an OpenSpec or package update, run the installer again to refresh the
user-level copy. The installer replaces only the package-owned install
directory and the package-owned skill and helper names.

## Bootstrap a repository

`custom-openspec-init` prepares a repository without replacing the `openspec`
executable.

Run it from a repository path:

```text
custom-openspec-init .
```

The helper performs these actions:

1. It reads the target before it writes.
2. It refuses a target that uses a schema other than `spec-driven`.
3. It enables the supported custom profile and adds the `verify` workflow when
   the current profile does not expose it.
4. It runs normal `openspec init` for a new repository.
5. It uses additive normal `openspec init` for an initialized repository that
   lacks the native Verify skill.
6. It merges the package policy into `openspec/config.yaml`.
7. It validates the resulting OpenSpec files.
8. It reports changed files and configuration entries.

The helper keeps project context, project rules, unknown project fields,
generated OpenSpec files, and user-owned files. It adds missing policy entries
only. A repeated run keeps one effective package entry and reports no package
changes.

The helper writes the global workflow profile only when the native Verify
workflow is missing. It keeps existing workflow choices and adds `verify`. If
Codex uses command-only delivery, the helper changes delivery to `both` so the
skill can be installed. It records this change.

If setup fails after changes start, the helper restores its changed target and
global files. It does not replace a malformed configuration. It reports that
the operation rolled back.

Use JSON output when another script needs the result:

```text
custom-openspec-init . --json
```

The helper does not create a root-level `grill.md`, a custom schema artifact,
or a replacement OpenSpec command.

## Use Grill Me when it helps

Grill is optional. Use normal Explore or Propose for a trivial or already
specified change. Use `custom-openspec-grill` when the change has unclear
intent, hidden constraints, important decisions, tradeoffs, UX concerns,
security concerns, or other requirements that need deeper discussion.

The adapter delegates the question process to the installed upstream
`grill-me` skill. It does not ask its own question series. It does not perform
implementation work.

After the upstream session returns its distilled result, the adapter keeps
these sections in `grill.md`:

- Intent.
- Constraints.
- Decisions.
- Assumptions Surfaced.
- Open Questions.
- Non-Goals or Out of Scope.

Resolved decisions stay in Decisions. Unresolved items stay in Open Questions.
The attached file is supplemental planning context. It is not a schema
artifact.

### Grill before a change exists

The upstream skill writes source material in `.grill`. Stage that source in a
user-level location before a named OpenSpec change exists:

```text
custom-openspec-grill stage --source .grill/<source-file>.md
```

The command copies the source outside the repository and reports a stable
session identity. The identity includes the source content and path. It does
not depend only on the generated filename slug.

The default staging path is:

```text
~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/
```

Set `CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME` when you need another user-level
staging path. The source file in `.grill` remains unchanged.

### Attach Grill to a named change

After Propose creates a named change, attach the staged session:

```text
custom-openspec-grill attach \
  --change add-example \
  --session <session-id>
```

The command writes `openspec/changes/add-example/grill.md`. The file records the
source session, source path, source hash, capture time, and upstream skill.

If the change already has `grill.md`, the command stops and requests a user
choice. Use `--replace` or `--combine` only after the user chooses that action.
Attaching the same session again is idempotent and reports the existing
attachment.

## Lifecycle

The normal lifecycle is:

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
      +--> coherent implementation groups
      |        |
      |        +--> automated tests when applicable
      |        +--> re-anchor as needed
      |        +--> required UAT when applicable
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

The host can use the Codex names `$openspec-propose`,
`$openspec-apply-change`, `$openspec-update-change`,
`$openspec-verify-change`, and `$openspec-archive-change` for the native
generated skills.

The normal order is Apply, required or waived UAT, Verify, then Archive.
Guidance recommends this order. Native OpenSpec behavior and explicit user
decisions remain authoritative.

## Apply or Update

Use Apply when the plan remains correct and the implementation does not meet
the plan. Examples include a coding defect, a failed implementation test,
incorrect behavior, or a missing implementation task that does not change the
agreed intent.

Use Update when the proposal, specification, or design is incomplete,
incorrect, contradictory, or no longer describes the desired behavior.
Examples include a new architectural constraint, omitted behavior, a change
in scope, or a changed user expectation.

When Apply finds a planning problem, stop and report it. Use Update to change
the planning artifacts. Then return to Apply. Do not change planning intent
silently during implementation.

## Tasks and tests

The package uses the stock `tasks.md` file. It does not add a scheduler,
worker fields, fixed execution waves, or static parallel-safety fields.

Group related tasks into coherent areas. Order tasks by useful dependencies.
Mark a task complete when its specified behavior is complete. Run focused
automated checks at the end of each coherent group.

When changed behavior is reasonably unit-testable, add or update a suitable
unit test. Test-Driven Development is not required. Implementation can come
before tests.

Prefer project-native automated checks. These checks include unit, integration,
functional, API, UI, browser, static analysis, lint, compilation, and build
checks. Do not add manual work that duplicates reliable automation.

The package policy is advisory. It directs work but does not replace native
OpenSpec commands or hard-enforce a result.

## Human UAT

Human user acceptance testing, or Human UAT, applies when automation cannot
reasonably establish an acceptance criterion. Examples include subjective
appearance, interaction quality, UX expectations, unavailable hardware, or
user confirmation of intent.

When UAT applies, add each independently invalidatable scenario as its own
normal checkbox in `tasks.md`. Apply pauses at an incomplete UAT task and gives
the user manual steps and expected results.

Only the user can provide the disposition:

```text
[x] HUMAN UAT - PASSED: Confirm the modal opens and closes with the keyboard.
[x] HUMAN UAT - WAIVED BY USER: Confirm the modal opens and closes with the keyboard.
```

`PASSED` records a user confirmation. `WAIVED BY USER` records an explicit user
exception. The agent cannot self-pass UAT, infer acceptance, or infer a
waiver. The agent cannot apply an automatic waiver.

Do not add UAT when reliable automation establishes the criterion. Record why
UAT does not apply in the task or acceptance record:

```text
HUMAN UAT - NOT APPLICABLE: covered by the automated contract tests.
```

This record is not `HUMAN UAT - PASSED` or `HUMAN UAT - WAIVED BY USER`. It is
not a checkbox and does not create a manual task. If the user requests Archive
while required UAT remains incomplete, name each scenario and ask the user to
perform it or explicitly waive it.

A Verify finding alone does not invalidate UAT. After a substantive
implementation change, assess each passed or waived scenario. Reopen only the
scenarios that the change can affect. A change that affects waived behavior
also invalidates the waiver. Unrelated passed or waived scenarios remain
resolved.

## Verify

Verify is a workflow review. It is not a checkbox in `tasks.md` and it is not a
package artifact.

After Apply tasks and applicable UAT tasks are resolved, run the native Verify
workflow before Archive:

```text
$openspec-verify-change
```

Verify compares requirements, scenarios, tasks, automated test results, and
applicable UAT results. It reports gaps instead of calling the change ready
when required evidence is missing.

A Verify result applies only to the substantive implementation state that it
inspected. A later substantive implementation change makes the result stale.
The next path is Apply, affected UAT when invalidated, and Verify again.

A non-substantive change can retain Verify only when it cannot affect
implementation correctness. Run Verify again when that effect is uncertain.
A Verify finding without an implementation change does not invalidate UAT.

## Archive

Before normal Archive, the guidance assesses these conditions:

1. Normal implementation tasks are complete.
2. Required Human UAT is `PASSED` or `WAIVED BY USER`.
3. No passed or waived scenario was affected by later implementation.
4. Verify covers the latest substantive implementation state.

If Verify is missing, stale, or uncertain, run Verify before Archive. If UAT is
incomplete, name the scenarios. The user must pass or explicitly waive each
scenario before Archive is treated as ready.

This guidance is advisory. It does not hard-enforce native Archive behavior.
Native task protection and explicit user choices remain authoritative.

## Re-anchor during Apply

Re-anchoring means refreshing the agent's understanding from persisted OpenSpec
state instead of relying on old conversation context.

Use a lightweight re-anchor at a coherent task group boundary. Refresh:

- Current task progress.
- Completed and remaining tasks.
- Current Apply state.
- Current operation guidance.
- The next coherent work group.

Use the native fresh Apply instruction for this refresh. Do not reread every
planning artifact or the whole repository after every task without a reason.

Use a full re-anchor after an interruption, an OpenSpec Update, a planning
artifact change, a material assumption or design problem, delegated work that
affects later implementation, or a conflict between code and the plan. Reread
the relevant planning artifacts and current repository context.

Delegation is optional. The package does not require subagents or one worker
per task.

## Source isolation

OpenSpec change folders isolate planning artifacts. They do not isolate source
code. Git owns branches, worktrees, commits, merges, rebases, and source
conflict resolution.

Use a Git branch or worktree when work pauses for another change, an urgent fix
is needed, or independent changes have partial source modifications. This
package does not create or manage branches or worktrees.

## Upgrades

### OpenSpec

Use the normal OpenSpec upgrade path:

1. Upgrade to the selected published OpenSpec release.
2. Run `openspec update` in the target repository.
3. Read the release changes for configuration, skills, and workflows.
4. Confirm that `spec-driven`, project configuration, operation guidance, and
   the Verify workflow still work.
5. Run this package's tests and smoke checks.

The package has no vendored schema copy. It does not require a schema merge.
If a future requirement needs a schema fork or a replacement command, stop and
record a new feasibility decision before adding it.

### Grill Me

Upgrade the upstream `grill-me` skill independently. Leave that skill
unchanged. Run the compatibility command with a representative source file:

```text
custom-openspec-grill compatibility \
  --source .grill/example.md \
  --json
```

The command discovers the installed `grill-me` skill in the Codex user-level
skills directory. Use `--skills-dir` when the skill is in another supported
test location.

The command uses temporary state. It stages a source file, attaches it to a
temporary change, repeats the attachment, and reads the resulting context.
It reports the dependency, required sections, source traceability, attachment
idempotence, optional use, and no-implementation evidence. It also reports
whether the source and upstream skill stayed unchanged.

The command uses semantic headings. It does not depend on exact prompt
wording, line positions, or filename slug formatting. If the dependency or
any contract evidence is missing, the command returns a failure and reports
the missing evidence.

## Planning artifacts and deliverables

The proposal, specifications, design, and `tasks.md` inside an OpenSpec change
are planning artifacts. They describe intent and work. They are not the
user-level package files.

The package deliverables are the policy, bootstrap, Grill adapter, support
scripts, tests, fixtures, compatibility record, and README.

`grill.md` is supplemental context that belongs with a named change. It is not
part of the stock artifact graph. Verify is a workflow review. It is not a
task or package file.

## Troubleshooting

### Verify is not available

Run `openspec config list --json` and confirm that the effective profile
contains `verify`. Then run `openspec update` in the target repository. Run
`custom-openspec-init` again if the generated Codex Verify skill is missing.

### Verify is stale

A substantive implementation change after Verify makes the result stale. Run
Apply again, repeat only affected UAT scenarios, and run Verify again.

### UAT is incomplete

Read the incomplete UAT task. Follow its manual steps. Ask the user to record
`HUMAN UAT - PASSED` or `HUMAN UAT - WAIVED BY USER`. Do not infer either value.

### Archive is requested with UAT outstanding

Name each outstanding scenario. Ask the user to perform it or explicitly waive
it. Record each waiver in `tasks.md` before treating Archive as ready.

### The plan does not match the repository

Use Apply when the plan is correct and implementation is wrong. Use Update
when the plan no longer describes the intended behavior. Stop before silently
changing the plan.

### Grill output is missing

Confirm that the upstream `grill-me` skill is installed in the supported
user-level skill directory. If the source exists in `.grill`, run `stage` and
record the reported session identity. Attach that identity after a named
OpenSpec change exists.

### Bootstrap repeats changes

Run `custom-openspec-init . --json`. Read the changed entries. If an existing
configuration has duplicate project entries, the helper reports them and does
not delete user-owned values. Remove an unintended project duplicate by an
explicit user edit, then run the helper again.

### The target uses another schema

Stop. This package supports the stock `spec-driven` schema. Do not let the
helper replace a project schema. Use the project's own workflow or record a new
feasibility decision.

## Quality boundary and non-goals

The package stays small, inspectable, version-controlled, idempotent where
needed, conservative with project configuration, and easy to remove.

This version does not implement:

- A custom OpenSpec schema.
- `verification.md`.
- A custom Apply skill.
- A custom Verify skill.
- A custom Archive implementation.
- A replacement lifecycle.
- A task scheduler or CP-SAT scheduler.
- Fixed execution waves or static parallel-safety metadata.
- Mandatory subagents.
- TDD enforcement.
- Automatic Git branch or worktree management.
- Automatic UAT waiver.
- Changes to upstream Grill Me.
- Changes to OpenSpec-generated skills or OpenSpec source.

If a requirement needs one of these items, stop implementation. Record the
limitation and request a new decision.

## Test the package

Run the unit tests from the repository root:

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The tests cover policy merge, idempotence, rollback, non-stock schema refusal,
Grill staging, semantic attachment, required sections, and repeated
attachment.

The disposable validation matrix must cover these scenarios:

1. Simple change with no unnecessary Grill or UAT.
2. Automated-only change with Propose, Apply, automated tests, Verify, and
   Archive.
3. Human UAT with independent tasks, an Apply pause, user disposition, and
   Verify after UAT.
4. Explicit UAT waiver with `WAIVED BY USER` distinct from `PASSED`.
5. UAT failure that separates Apply from Update.
6. Verify finding without UAT invalidation until implementation changes.
7. Selective invalidation of only affected UAT.
8. Invalidation of a waiver after a relevant substantive change.
9. Lightweight and full re-anchoring.
10. Premature Archive with missing or stale Verify and incomplete UAT.
11. Repeated bootstrap with preserved context and no duplicate policy.
12. OpenSpec and Grill Me upgrade smoke tests.

Run the package validation command and OpenSpec validation after an upgrade:

```text
PYTHONPATH=src python3 -m unittest discover -s tests -v
openspec validate --all --json --no-interactive
openspec status --change add-user-level-openspec-customization --json
```

The package does not modify generated `openspec-*` skills or OpenSpec source.
