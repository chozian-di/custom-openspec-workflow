# Spec Delta

## ADDED Requirements

### Requirement: Acknowledge missing OpenSpec before package installation

When the installer cannot find the default `openspec` command on `PATH`, it
SHALL tell the user that this workflow cannot function until OpenSpec is
installed. The missing command SHALL remain a non-blocking package
installation prerequisite.

For a non-dry-run install, the installer SHALL get explicit acknowledgment
before it writes user-level files unless the user passes `-y` or `--yes`.
The `-y` and `--yes` options SHALL count as explicit acknowledgment. Existing
ownership and conflict checks SHALL continue to apply.

#### Scenario: Interactive install finds missing OpenSpec

- **WHEN** a user runs an interactive install and `openspec` is not on `PATH`
- **THEN** the plan and confirmation prompt state that the workflow cannot
  function until OpenSpec is installed, and the prompt asks whether to
  continue with package installation

#### Scenario: User declines the missing OpenSpec acknowledgment

- **WHEN** a user declines the acknowledgment or provides no interactive answer
- **THEN** the installer reports cancellation and changes no user-level path

#### Scenario: The user passes `--yes` with missing OpenSpec

- **WHEN** a user runs an install with `--yes` and no file conflict exists
- **THEN** the installer treats the option as explicit acknowledgment and
  installs the package without installing OpenSpec

#### Scenario: A dry run finds missing OpenSpec

- **WHEN** a user runs an install with `--dry-run` and `openspec` is missing
- **THEN** the result reports the warning and changes no user-level path

#### Scenario: JSON install reports the acknowledgment

- **WHEN** a user runs an interactive JSON install and `openspec` is missing
- **THEN** the plan and acknowledgment prompt go to standard error, and the
  final result remains one valid JSON object on standard output

### Requirement: Give users external OpenSpec installation guidance

When OpenSpec is missing, installer output and `README.md` SHALL direct the
user to install it outside this project. The guidance SHALL include the
following commands:

```text
npm install -g @fission-ai/openspec@latest
openspec --version
```

The guidance SHALL also explain that a user can pass
`--openspec-executable /path/to/openspec` when the executable is installed
outside `PATH`. The installer MUST NOT invoke a package manager or modify an
OpenSpec installation.

#### Scenario: Missing OpenSpec includes install guidance

- **WHEN** the installer reports that `openspec` is missing
- **THEN** the output includes the external install command, the version
  check, and the explicit executable override

#### Scenario: The README documents external installation

- **WHEN** a user reads the prerequisite section of `README.md`
- **THEN** the user can install OpenSpec, check the installed command, use an
  executable outside `PATH`, and see that this project does not install it
