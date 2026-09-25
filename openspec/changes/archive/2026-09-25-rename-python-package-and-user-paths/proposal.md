# Proposal

## Why

The project distribution is named `custom-openspec-workflow`, but its Python
package, user data directory, and environment variables use the shorter
`custom-openspec` name. This creates different names for the same project.
The project has no installed users, so it can use one naming scheme before its
first release.

## What Changes

- **BREAKING** Rename the Python package from `custom_openspec` to
  `custom_openspec_workflow`.
- Update Python imports, package resource lookups, package data, entry point
  targets, tests, and source paths.
- Keep the distribution name `custom-openspec-workflow`.
- Rename the project environment variables to the
  `CUSTOM_OPENSPEC_WORKFLOW_*` namespace.
- **BREAKING** Change the default install directory to
  `~/.local/share/custom-openspec-workflow/custom_openspec_workflow/`.
- Change the default Grill staging directory to
  `~/.local/share/custom-openspec-workflow/grill/`.
- Keep the `custom-openspec-init`, `custom-openspec-grill`, and
  `custom-openspec-install` command names.
- Keep the `custom-openspec-grill` skill name.
- Keep all existing OpenSpec capability IDs.
- Update the README and tests to describe and check the new names and paths.
- Do not add migration behavior or compatibility aliases for the old names.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-level-openspec-policy`: Use the renamed Python package, environment
  variable namespace, and user-level install directory while keeping the
  public command and skill names.
- `custom-openspec-grill`: Use the new default user-level staging directory
  and environment variable namespace.

## Impact

The change affects the `src/custom_openspec` package directory, Python module
imports, `pyproject.toml`, installer wrapper targets, host discovery, Grill
staging defaults, tests, and `README.md`. It does not add a dependency or
change OpenSpec capability IDs. It does not change the upstream Grill Me
skill or the stock OpenSpec schema.
