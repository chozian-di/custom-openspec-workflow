# user-level-openspec-policy Specification

## Purpose

This capability provides one reusable user-level OpenSpec customization package. It targets brownfield software development and adds policy and guidance across repositories while keeping OpenSpec's lightweight, fluid stock workflow and its upstream ownership. It minimizes maintenance burden and remains resilient to future OpenSpec and Grill Me upgrades.

## Requirements

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

The package SHALL provide a canonical policy or configuration source,
`custom-openspec-init`, `custom-openspec-grill`, only necessary support
scripts, and a comprehensive `README.md`. A user MUST be able to use the
package across repositories without copying policy files or skills into each
target repository. When the user does not provide an install directory, the
installer SHALL place the Python package under
`~/.local/share/custom-openspec-workflow/custom_openspec_workflow/`. Host
configuration variables SHALL use the `CUSTOM_OPENSPEC_WORKFLOW_*` namespace.

#### Scenario: User installs the package

- **WHEN** the user installs the customization on the supported coding-agent host
- **THEN** the user can discover and use `custom-openspec-init` and `custom-openspec-grill` from user-level locations without copying them into each target repository

#### Scenario: The default package layout is used

- **WHEN** the user installs the package without an explicit install directory
- **THEN** the installed Python package is available at `~/.local/share/custom-openspec-workflow/custom_openspec_workflow/` and the generated helpers load that package

#### Scenario: The host has different user-level locations

- **WHEN** the supported host uses specific user-level skill or executable locations
- **THEN** installation discovers and reports those locations instead of assuming a layout used by another host

#### Scenario: Host configuration uses the project namespace

- **WHEN** the user sets host discovery variables
- **THEN** the installer reads `CUSTOM_OPENSPEC_WORKFLOW_HOST`, `CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR`, and `CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR`

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
+
### Requirement: Present and confirm user-level install operations

`custom-openspec-install` SHALL build and display a complete plan before it
changes a user-level path. The plan SHALL identify every file and directory
operation, including package files, the custom skill, helper wrappers, the
ownership manifest, and safe directory cleanup. The plan SHALL identify create,
replace, preserve, conflict, and remove actions.

The installer SHALL ask for confirmation after it displays the plan unless the
user passes `-y` or `--yes`. Both options SHALL apply to install and uninstall.
They SHALL skip only the confirmation prompt and SHALL NOT bypass ownership or
conflict checks.

For a JSON operation that can write files, the installer SHALL write the
complete plan to standard error before the confirmation prompt or automatic
apply. It SHALL write the final operation result as one valid JSON object to
standard output.

#### Scenario: Install displays all planned changes

- **WHEN** the user runs `custom-openspec-install` without `-y` or `--yes`
- **THEN** the installer displays every user-level path that the install can
  create or replace and asks the user to confirm before it writes

#### Scenario: User declines an install

- **WHEN** the user declines the install confirmation
- **THEN** the installer reports that the operation was cancelled and leaves all
  user-level paths unchanged

#### Scenario: Yes bypasses install confirmation

- **WHEN** the user runs the install with `-y` or `--yes` and no conflict exists
- **THEN** the installer applies the planned user-level changes without asking a
  confirmation question

#### Scenario: Dry run does not change files

- **WHEN** the user runs the install with `--dry-run`
- **THEN** the installer displays or returns the complete plan and changes no
  user-level path

#### Scenario: Non-interactive install requires explicit confirmation bypass

- **WHEN** the installer has no interactive input and the user does not pass
  `-y` or `--yes`
- **THEN** the installer stops before writing and reports that explicit
  confirmation bypass is required

#### Scenario: JSON plan precedes interactive confirmation

- **WHEN** the user runs `custom-openspec-install --json` without `-y` or
  `--yes` with interactive input
- **THEN** the installer writes the complete plan to standard error before the
  confirmation prompt, writes no user-level path before confirmation, and
  returns the final result as valid JSON on standard output

#### Scenario: JSON plan precedes automatic apply

- **WHEN** the user runs `custom-openspec-install --json` with `-y` or `--yes`
- **THEN** the installer writes the complete plan to standard error before it
  applies changes and writes the final result as one valid JSON object to
  standard output

### Requirement: Track and protect package-owned user-level files

The installer SHALL record the user-level paths that it owns and the installed
content hash for each path. On a later install, it SHALL update a recorded path
when its current content still matches the recorded installed content.

An empty target with no existing package files, custom skill, wrappers, or extra
files under the package or custom skill directories SHALL be valid for a fresh
install. If any of those paths exist without a trustworthy ownership manifest,
the installer MUST report an unmanaged conflict before any install write. With
a trustworthy manifest, the installer MUST refuse an unmanaged existing path or
a recorded path whose content changed outside the installer. It SHALL report
the conflict before any install write. During uninstall, it SHALL preserve and
report a changed managed path while it removes other unchanged managed files.
`-y` and `--yes` SHALL NOT override install conflict refusal or cause removal of
a changed path.

#### Scenario: Fresh install records ownership

- **WHEN** the user confirms an install into empty target locations
- **THEN** the installer creates the package files, skill, wrappers, and
  ownership manifest and records their installed content hashes

#### Scenario: Repeated install updates owned files

- **WHEN** the user installs a newer package and each existing managed file still
  matches its recorded installed content
- **THEN** the installer can replace the managed files and updates the manifest
  without treating the files as user conflicts

#### Scenario: Unmanaged path blocks install

- **WHEN** a trustworthy ownership manifest exists and an install target already
  contains a path that the manifest does not identify as package-owned
- **THEN** the installer reports a conflict and makes no install changes

#### Scenario: Existing files without ownership manifest block install

- **WHEN** an install target contains package files, the custom skill, a
  wrapper, or an extra file under the package or custom skill directories
  without a trustworthy ownership manifest
- **THEN** the installer reports a conflict and makes no install changes

#### Scenario: User-modified path blocks install

- **WHEN** a package-owned path differs from the content recorded in the
  manifest
- **THEN** the installer reports a conflict and makes no install changes

### Requirement: Uninstall only package-owned user-level files

`custom-openspec-install --uninstall` SHALL plan and remove only unchanged files
that the ownership manifest identifies as package-owned. It SHALL preserve
modified managed files and report each preserved path. It SHALL not remove the
user-level data root, unrelated files, Grill staging sessions, source files,
repositories, repository OpenSpec configuration, or OpenSpec global
configuration.

#### Scenario: Confirmed uninstall removes the package

- **WHEN** the user confirms `custom-openspec-install --uninstall` and all
  managed files retain their recorded content
- **THEN** the installer removes the package files, custom skill, wrappers, and
  manifest while preserving unrelated user-level data

#### Scenario: Modified file is preserved during uninstall

- **WHEN** a managed file differs from its recorded content during uninstall
- **THEN** the installer preserves the file, reports the path, and does not
  delete the user modification

#### Scenario: Uninstall does not roll back repository setup

- **WHEN** the user uninstalls the user-level package after running
  `custom-openspec-init` in a repository
- **THEN** the repository files, OpenSpec configuration, OpenSpec global
  configuration, and generated repository skills remain unchanged

#### Scenario: Missing ownership record stops removal

- **WHEN** the selected install root has no trustworthy ownership manifest
- **THEN** the installer refuses to guess which files it can remove and leaves
  all paths unchanged

### Requirement: Keep generated Python bytecode in the user cache

The package SHALL keep persistent Python source files and generated Python
bytecode in separate user-level locations. Python bytecode is compiled `.pyc`
file data. When the user does not set `PYTHONPYCACHEPREFIX`, the package SHALL
use `~/.cache/custom-openspec-workflow` as the bytecode cache root. The package
SHALL keep the installed Python package and ownership manifest under
`~/.local/share/custom-openspec-workflow`.

Installed helpers and repository shell launchers SHALL set
`PYTHONPYCACHEPREFIX` before Python imports the package. When the user sets
`PYTHONPYCACHEPREFIX`, the helpers SHALL use that value instead of the default.

The bytecode cache SHALL remain outside the installer ownership manifest and
the install and uninstall file scope.

#### Scenario: Default installed helper cache

- **WHEN** the user installs the package without `PYTHONPYCACHEPREFIX` and
  runs an installed helper
- **THEN** the helper loads source files from
  `~/.local/share/custom-openspec-workflow` and writes generated `.pyc` files
  under `~/.cache/custom-openspec-workflow` without creating package-local
  `__pycache__` files

#### Scenario: User-selected cache prefix

- **WHEN** the user sets `PYTHONPYCACHEPREFIX` before running an installed
  helper or repository shell launcher
- **THEN** the helper uses the selected cache prefix and does not replace it
  with the package default

#### Scenario: Repository launcher cache

- **WHEN** the user runs a repository shell launcher without an explicit
  `PYTHONPYCACHEPREFIX`
- **THEN** the launcher uses `~/.cache/custom-openspec-workflow` before it
  imports package modules

#### Scenario: Uninstall leaves generated cache data outside its scope

- **WHEN** the user uninstalls the package after a helper creates bytecode
  cache data
- **THEN** uninstall removes only unchanged manifest-owned files and does not
  remove or claim ownership of the bytecode cache
