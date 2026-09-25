# Spec Delta

## ADDED Requirements

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
