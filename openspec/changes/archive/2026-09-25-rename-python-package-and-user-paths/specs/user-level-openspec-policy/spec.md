# Spec Delta

## MODIFIED Requirements

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
