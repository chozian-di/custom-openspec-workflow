# Custom OpenSpec workflow

The official project name is `custom-openspec-workflow`. Its short name is
`COW`, and it is also known as "chozian's OpenSpec Workflow".

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

The upstream Simple English skill owns its writing rules. This package only
looks for `skills/simple-english/SKILL.md`. It does not copy, install, update,
or remove that skill.

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

The installer shows a plan before it changes a user-level path. The plan lists
created, replaced, preserved, conflicting, and removed paths. The installer
asks for confirmation after it shows the plan.

The installer places these files in user-level locations:

- `~/.agents/skills/custom-openspec-grill/SKILL.md`.
- `~/.local/bin/custom-openspec-init`.
- `~/.local/bin/custom-openspec-grill`.
- `~/.local/share/custom-openspec-workflow/custom_openspec_workflow`.
- `~/.local/share/custom-openspec-workflow/manifest.json`.

Use `-y` or `--yes` when the command must run without a confirmation prompt:

```text
./scripts/custom-openspec-install \
  --host codex \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --yes
```

The two options have the same effect. They skip the prompt. They do not skip
ownership or conflict checks.

Use `--dry-run` to display the plan without changing files:

```text
./scripts/custom-openspec-install \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --dry-run
```

Use `--json` when another program needs the plan or the result. A write-mode
JSON command writes the complete plan to standard error before confirmation or
apply. It writes the final result object to standard output. A JSON dry run
writes its result object, which includes the plan, to standard output. In
interactive JSON mode, the prompt is also written to standard error. For a
non-interactive command, add `-y` or `--yes`.

```text
./scripts/custom-openspec-install \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --dry-run \
  --json

./scripts/custom-openspec-install \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --yes \
  --json
```

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

The persistent package path is `<install-dir>/custom_openspec_workflow`. The
installer keeps Python source files and the ownership manifest there.

Python bytecode is compiled `.pyc` file data. When
`PYTHONPYCACHEPREFIX` is not set, installed helpers and repository launchers
use `~/.cache/custom-openspec-workflow` for this data. They set the cache path
before Python starts. The cache can also contain bytecode for imported Python
dependencies.

Set `PYTHONPYCACHEPREFIX` when you need another cache path. The helpers keep
the value that you set:

```text
PYTHONPYCACHEPREFIX=/tmp/custom-openspec-cache \
  ./scripts/custom-openspec-grill --help
```

The ownership manifest is a JSON file at `<install-dir>/manifest.json`. It
records each package-owned file, its content hash, its file mode, and the
directories that the installer created. The installer uses this record during
later installs and during uninstall.

If an existing target is not in the manifest, the installer reports a conflict
and writes nothing. If a managed file changed after installation, the
installer reports a conflict and writes nothing. `-y` and `--yes` do not
override these checks.

Run the installer again after a package update. The installer replaces a
managed file only when its current content still matches the manifest. It can
remove an old managed file during an upgrade when that file is unchanged.

To remove the user-level package, run:

```text
./scripts/custom-openspec-install \
  --host codex \
  --install-dir ~/.local/share/custom-openspec-workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --uninstall
```

Use `--yes` for a non-interactive uninstall. Uninstall removes only unchanged
files in the ownership manifest. It preserves modified files and reports each
preserved path. It also removes empty directories that the installer created.
It keeps the install root, unrelated files, Grill staging sessions, and the
upstream `grill-me` and `simple-english` skills. It does not remove files from
`~/.cache/custom-openspec-workflow` or from a path that you set with
`PYTHONPYCACHEPREFIX`.

If the ownership manifest is missing or invalid, uninstall refuses to guess
which files it can remove. It leaves all paths unchanged.

User-level uninstall does not reverse repository bootstrap. It does not remove
`custom-openspec-init` changes from a repository. It does not edit repository
source files, `.agents`, `openspec`, or OpenSpec global configuration. Change
those repository files separately when that cleanup is required.

## Install prerequisites

The installer checks known prerequisites when it builds an install plan. These
checks read the selected skills directory and the command search path. They do
not install or change a prerequisite.

The checks are advisory. An advisory warning informs you about a missing
feature dependency. It does not stop a safe package install.

For an install or dry run, the installer checks these prerequisites:

- The selected Codex skills directory for `grill-me/SKILL.md`. The
  `custom-openspec-grill` feature uses this upstream skill for Grill sessions.
- The selected Codex skills directory for `simple-english/SKILL.md`. This
  optional skill helps write project documentation.
- The default `openspec` command on `PATH`. The `PATH` setting lists directories
  that contain commands. The `custom-openspec-init` feature uses this command
  for repository bootstrap.

If the upstream Grill Me skill is missing, the plan names the checked skills
directory and reports a warning. Install `skills/grill-me` from
`satya-janghu/agent-skills` with the host method that you use. Read the
instructions in this README before you install the skill. The package does not
install or change Grill Me.

If the upstream Simple English skill is missing, the plan names the checked
skills directory and reports a warning. Install only the `skills/simple-english`
skill from `AminBlg/SimpleEnglish` with the skills CLI:

```text
npx skills add AminBlg/SimpleEnglish
```

This command installs the skill only. It does not install the upstream session
hook or output style. The package does not install, update, or remove Simple English.
It only reports whether `simple-english/SKILL.md` is available.

If the default `openspec` command is missing, the plan reports a warning. The
bootstrap helper accepts an explicit executable path:

```text
custom-openspec-init . --openspec-executable /path/to/openspec
```

The plan shows missing prerequisite warnings before a human confirmation
prompt. A JSON write-mode plan goes to standard error before confirmation or
apply. The final JSON result goes to standard output. Both JSON objects include
the `prerequisites` results. A JSON dry run includes the same results in its
standard output and does not change files.

The installer does not run prerequisite checks during uninstall. Uninstall
does not remove the upstream `grill-me` or `simple-english` skills or other
user-owned files.

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

Explore discussion and repository investigation are the normal first steps.
Grill is optional. Continue to Propose without Grill Me when Explore provides
enough clarity.

Run `custom-openspec-grill` when important requirements remain unresolved. Use
it for unclear intent, hidden constraints, important decisions, tradeoffs, UX
concerns, security concerns, or other requirements that need deeper discussion.

Grill Me surfaces unclear intent, hidden constraints, decisions, tradeoffs,
non-goals, and open questions before planning. It gives the planning process a
clear record of what the user needs, what the repository must preserve, and
what remains unresolved. Use it when normal Explore does not resolve an
important requirement.

Grill-first is also available for a change with high uncertainty. Run Grill Me,
keep the pending handoff, use Explore to test the captured decisions against
the repository, and then use Propose.

The adapter delegates the question process to the installed upstream
`grill-me` skill. It does not ask its own question series. It does not perform
implementation work.

## Use Simple English for documentation

Simple English helps write clear documentation with short sentences, active
voice, and consistent terms. It applies plain language to READMEs, runbooks,
procedures, error messages, release notes, API guides, and other text for
readers outside the field. It also defines technical terms before it uses them
and keeps instructions in a clear order.

Simple English is optional. Use it when a document needs a plain style or when
readers do not share the writer's technical background. This package reports
the skill as an advisory prerequisite. It does not add Simple English rules to
OpenSpec configuration and does not install optional upstream plugin features.

### Recommended planning order

Use this order for a normal change:

1. Run `/opsx:explore` for discussion and repository investigation.
2. If important requirements remain unresolved, run `custom-openspec-grill`.
3. Use `/opsx:propose` as the normal writer of the initial planning artifacts.
4. After Propose creates the named change, attach the pending session before the initial artifacts are written.
5. Continue with normal OpenSpec planning and implementation.

OpenSpec 1.13.2 does not provide a supported Explore guidance field. This
package cannot block native Explore from creating or updating planning
artifacts after the user explicitly confirms those writes. If Explore writes an
artifact before Grill runs, do not claim that it used Grill context. Do not
rewrite that artifact automatically after attachment. Use OpenSpec Update when
the user wants to reconcile the artifact with the attached context.

### Check the `.grill/` ignore rule

Before you invoke Grill Me or use a source under the repository's `.grill/`
directory, run:

```text
git -C <repository> check-ignore -q -- .grill/
```

If the command does not confirm that `.grill/` is ignored, stop. Tell the user
to add `.grill/` to `<repository>/.gitignore`. The skill does not edit
`.gitignore`, invoke Grill Me, stage a source, or attach a session when this
preflight fails.

### Grill before a change exists

After the upstream session returns, use its exact source path. Do not rebuild a
path from a generated filename slug. Do not choose a source only because it
has the newest timestamp.

If the upstream result has no exact source path, use source discovery only when
exactly one plausible source exists. If more than one plausible source exists,
ask the user to select the source. Do not stage a source before the selection.

After source selection, stage the source through the AI session:

```text
custom-openspec-grill stage \
  --source <exact-source-path> \
  --json
```

The JSON result includes a stable `sessionId`, the exact `sourcePath`, and the
`stagingDir`. Keep those values and the repository root as a pending handoff in
the active AI session. Keep the handoff until attachment or until the user
chooses not to continue.

The command copies the source outside the repository. The default staging path
is:

```text
~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/
```

Set `CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME` when you need another user-level
staging path. The source file in `.grill` is a read-only snapshot. Do not edit
or delete it.

### Attach Grill to a named change

When a named change exists, attach the pending session before the next planning
artifact that uses Grill context. In the recommended Propose flow, attach
after Propose creates the named change and before Propose writes `proposal.md`
or another initial planning artifact:

```text
custom-openspec-grill attach \
  --root <repository> \
  --change <change-name> \
  --session <session-id> \
  --json
```

If exactly one applicable named change exists, select it automatically.
When more than one applicable named change exists, ask the user to select the change.
Never attach to an arbitrary change.

The command writes `openspec/changes/<change-name>/grill.md`. The file records
the source session, source path, source hash, capture time, and upstream skill.
It is a read-only snapshot. Record later decisions in the normal OpenSpec
artifacts. The latest explicit user decision takes precedence over a
conflicting Grill summary or snapshot.

If the change already has `grill.md` for another session, preserve the existing
context and ask the user whether to replace or combine it. Use `--replace` or
`--combine` only after the user chooses that action. Attaching the same session
again is idempotent and reports the existing attachment.

### Recovery and retention

If the active AI session ends after staging, use the recorded handoff to run
the attach command again. Include `--staging-dir <staging-root>` when the
session used a custom staging path. The source and session metadata remain
available until the user removes them.

Native Archive moves the complete named change, including `grill.md`, to:

```text
openspec/changes/archive/<date>-<change>/grill.md
```

Archive leaves the source under `.grill/` and the user-level staged session
under `~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/`.
Cleanup of these external files is a manual user action.

After you update this package, run the installer to deploy the updated
`custom-openspec-grill/SKILL.md` to the user-level skills directory:

```text
./scripts/custom-openspec-install \
  --host codex \
  --source-root src/custom_openspec_workflow \
  --skills-dir ~/.agents/skills \
  --bin-dir ~/.local/bin \
  --yes
```

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

## Lifecycle

The normal lifecycle is:

```text
Idea or problem
      |
      v
 /opsx:explore, discussion and repository investigation
      |
      +--> requirements clear, /opsx:propose
      |
      +--> requirements unresolved, custom-openspec-grill
                                      |
                                      v
                         pending handoff, then /opsx:propose
      |
      +--> Grill-first for high uncertainty, then Explore and Propose
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
