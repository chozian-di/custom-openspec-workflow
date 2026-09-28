# Spec Delta

## ADDED Requirements

### Requirement: Explain missing OpenSpec before bootstrap

Before `custom-openspec-init` invokes OpenSpec or changes repository or global
configuration, it SHALL check the selected OpenSpec executable. If the
executable is unavailable, the helper SHALL stop and report that this workflow
cannot function until OpenSpec is installed.

The error SHALL include the external installation command, the `openspec
--version` check, and the `--openspec-executable /path/to/openspec` override.
The helper SHALL leave the target repository and global configuration
unchanged.

#### Scenario: The default OpenSpec command is missing

- **WHEN** a user runs `custom-openspec-init` without an executable on `PATH`
- **THEN** the helper reports the missing command and installation guidance
  before it invokes OpenSpec or changes any target or global file

#### Scenario: An explicit OpenSpec executable is available

- **WHEN** a user passes `--openspec-executable` with a runnable OpenSpec
  executable
- **THEN** the helper uses that executable and does not report the default
  `PATH` command as missing

#### Scenario: An explicit OpenSpec executable is unavailable

- **WHEN** a user passes `--openspec-executable` with a path that cannot run
- **THEN** the helper reports that selected path and the same installation
  guidance without changing repository or global files
