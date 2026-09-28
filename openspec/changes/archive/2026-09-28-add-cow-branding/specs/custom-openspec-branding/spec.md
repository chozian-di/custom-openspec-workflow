# Spec Delta

## Purpose

This capability gives users one clear identity for the package across its README, commands, installer, metadata, and installed skill. It keeps the official project name separate from its alternate names.

## ADDED Requirements

### Requirement: Present official and alternate project names to users

Human-facing package surfaces SHALL identify `custom-openspec-workflow` as the official project name. They SHALL identify `COW` as the short name and state that the project is also known as "chozian's OpenSpec Workflow".

The README SHALL provide the fuller explanation. Package metadata, the top-level help for `custom-openspec-install`, `custom-openspec-init`, and `custom-openspec-grill`, human-readable installer output, and the installed `custom-openspec-grill` skill SHALL use a brief identity statement.

#### Scenario: A user reads the README

- **WHEN** a user reads the start of `README.md`
- **THEN** the README states that `custom-openspec-workflow` is the official name and identifies `COW` and "chozian's OpenSpec Workflow" as alternate names

#### Scenario: A user opens command help

- **WHEN** a user requests top-level help for `custom-openspec-install`, `custom-openspec-init`, or `custom-openspec-grill`
- **THEN** the help identifies the project with the official name, `COW`, and the alternate name in a brief form

#### Scenario: A user reads installer output

- **WHEN** the installer displays a human-readable plan, result, or refusal
- **THEN** the output includes a brief project identity reference without changing the operation details

#### Scenario: An agent reads the installed Grill skill

- **WHEN** the host loads the installed `custom-openspec-grill` skill
- **THEN** the skill identifies its package as `custom-openspec-workflow`, `COW`, and "chozian's OpenSpec Workflow" in a brief statement

### Requirement: Preserve machine-facing project identifiers

Branding text SHALL NOT rename or alter the existing command names, Python package import name, user-level paths, `CUSTOM_OPENSPEC_WORKFLOW_*` environment-variable namespace, ownership manifest format, or JSON output contract. The installer SHALL keep the identity text out of its machine-readable JSON plan and result unless a later requirement explicitly adds a versioned identity field.

#### Scenario: Existing commands and paths remain stable

- **WHEN** a user installs or runs the package after the branding change
- **THEN** the existing command names, import name, user-level paths, and environment-variable names remain unchanged

#### Scenario: JSON output remains machine-readable

- **WHEN** a user runs the installer with `--json`
- **THEN** the plan and final result remain valid JSON with the existing contract and do not include human-only branding text

#### Scenario: Ownership data remains compatible

- **WHEN** the installer updates an existing managed installation
- **THEN** the ownership manifest format and conflict checks continue to use the existing package identity and file paths
