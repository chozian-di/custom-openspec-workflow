# custom-openspec-init Specification

## Purpose

This capability prepares a repository to use the user-level policy while preserving normal OpenSpec initialization, the stock schema, project configuration, generated files, and user-owned files.

## Requirements

### Requirement: Bootstrap a new repository through normal OpenSpec

`custom-openspec-init` SHALL run or invoke normal `openspec init` behavior when a repository has no OpenSpec root. It SHALL retain the stock `spec-driven` schema, apply the customization policy, preserve generated OpenSpec files, and enable the supported workflow or profile needed for `/opsx:verify`.

#### Scenario: New repository setup

- **WHEN** the user runs `custom-openspec-init` in a repository without an OpenSpec root
- **THEN** the repository receives normal OpenSpec initialization, the customization policy, the stock `spec-driven` schema, and the supported Verify workflow

#### Scenario: Bootstrap does not replace upstream OpenSpec

- **WHEN** the helper prepares a new repository
- **THEN** it does not replace the `openspec` executable, disguise itself as upstream OpenSpec, or replace generated `openspec-*` skills

### Requirement: Extend an initialized repository safely

When a repository already has OpenSpec files, `custom-openspec-init` SHALL augment the repository in place without destructive reinitialization. It MUST preserve existing generated files, project context, project-specific rules, existing project configuration, and user-owned files.

#### Scenario: Existing repository setup

- **WHEN** the user runs `custom-openspec-init` in an initialized repository
- **THEN** the helper adds missing customization entries and leaves existing project content unchanged

#### Scenario: Project configuration contains context and rules

- **WHEN** the target `openspec/config.yaml` contains project context and project-specific rules
- **THEN** the resulting configuration retains those values and adds the customization without removing them

#### Scenario: Target uses a non-stock schema

- **WHEN** the target is not configured for the stock `spec-driven` schema
- **THEN** the helper reports that the stock customization boundary does not apply and does not silently replace the schema

### Requirement: Merge supported policy entries

The helper SHALL merge the canonical policy into `openspec/config.yaml` through supported OpenSpec configuration fields. It SHALL preserve existing project-owned values, add missing package rules and operation guidance, and avoid exact duplicate entries. Project-specific configuration SHALL remain possible after the merge.

#### Scenario: Fresh policy merge

- **WHEN** a valid stock configuration has no customization entries
- **THEN** the helper adds the package policy and operation guidance without removing existing supported values

#### Scenario: Existing policy merge

- **WHEN** the target already contains one or more matching package entries
- **THEN** the helper retains one effective copy of each entry and does not add duplicates

### Requirement: Roll back an unsafe customization

After the helper starts applying customization changes, a preflight, policy merge, Verify enablement, or validation failure SHALL restore files changed by the customization to their pre-run state. The helper SHALL leave unrelated user changes untouched, report the failure and rollback, and SHALL NOT leave a partial policy or partial workflow configuration.

#### Scenario: Policy merge fails

- **WHEN** the existing configuration cannot be read, parsed, or merged safely after customization changes begin
- **THEN** the helper restores the customization changes, preserves the original project configuration, and reports the rollback

#### Scenario: Result validation fails

- **WHEN** the resulting configuration fails the available OpenSpec validation or Verify enablement cannot be confirmed
- **THEN** the helper restores the customization changes, leaves unrelated files untouched, and reports that setup did not complete

### Requirement: Make repeated setup idempotent

`custom-openspec-init` SHALL produce the same effective configuration when the user runs it more than once with the same inputs. It SHALL not duplicate policy rules, operation guidance, workflow entries, or generated files.

#### Scenario: User repeats setup

- **WHEN** the user runs `custom-openspec-init` twice with the same inputs
- **THEN** the second run makes no unnecessary changes and the resulting configuration contains one effective copy of each customization entry

#### Scenario: User changes project configuration after setup

- **WHEN** the user adds project-specific context or rules after the first bootstrap
- **THEN** a later bootstrap preserves those values while retaining one effective copy of the package policy

### Requirement: Enable Verify through supported workflow configuration

The helper SHALL use the normal supported OpenSpec workflow or profile configuration to make `/opsx:verify` available. It SHALL preserve existing workflow choices and add only the missing Verify capability. It MUST NOT create a custom Verify implementation.

#### Scenario: Verify capability is missing

- **WHEN** the selected supported workflow or profile does not expose `/opsx:verify`
- **THEN** the helper adds the missing Verify capability without removing unrelated existing workflow choices

#### Scenario: Verify capability already exists

- **WHEN** the selected supported workflow or profile already exposes `/opsx:verify`
- **THEN** the helper keeps the existing configuration and does not add a duplicate workflow entry

### Requirement: Validate and report bootstrap results

After each run, `custom-openspec-init` SHALL validate the resulting OpenSpec configuration where the installed release supports validation. It SHALL report the files and configuration entries that it changed, including when it made no changes on an idempotent run.

#### Scenario: Valid setup completes

- **WHEN** the bootstrap completes without configuration errors
- **THEN** it reports the setup result and the target passes the available OpenSpec validation checks

#### Scenario: Configuration cannot be merged safely

- **WHEN** the target configuration cannot be read, parsed, or merged safely
- **THEN** the helper reports the error and does not replace the existing configuration with a partial result

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
