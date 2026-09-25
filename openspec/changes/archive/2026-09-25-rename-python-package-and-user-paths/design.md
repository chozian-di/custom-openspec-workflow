# Design

## Context

See `proposal.md` for the reason for this change.

The source package is now in `src/custom_openspec`. The distribution name in
`pyproject.toml` is `custom-openspec-workflow`. The installer copies the source
package into a user data directory and writes wrappers that import the copied
package. The host discovery code reads `CUSTOM_OPENSPEC_*` variables. Grill
staging uses a separate default under the same old user data directory.

The repository has no active change and no installed users. The change can
rename the package and configuration names without a compatibility layer.

## Goals / Non-Goals

Goals:

- Use `custom_openspec_workflow` for the source directory and Python imports.
- Keep `custom-openspec-workflow` as the distribution name.
- Use `CUSTOM_OPENSPEC_WORKFLOW_*` for project environment variables.
- Install the package under
  `~/.local/share/custom-openspec-workflow/custom_openspec_workflow/` by
  default.
- Stage Grill sessions under
  `~/.local/share/custom-openspec-workflow/grill/` by default.
- Keep command names, the skill name, and OpenSpec capability IDs stable.
- Keep explicit install and staging directory overrides available.

Non-Goals:

- Do not migrate or detect old user data.
- Do not support the old Python import package as an alias.
- Do not support the old environment variable names as aliases.
- Do not rename commands, the skill, or OpenSpec capability IDs.
- Do not change the stock OpenSpec schema or the upstream Grill Me skill.

## Decisions

### Rename the package as one unit

Rename `src/custom_openspec` to `src/custom_openspec_workflow`. Update all
relative and absolute imports, entry point targets, package data keys, resource
lookups, tests, and source paths together. Keep the package data subdirectory
`data/custom-openspec-grill` because it names a user-facing skill.

An import alias for `custom_openspec` is not needed. The project has no
installed users, and an alias would keep two names for one package.

### Centralize user data paths

Use one project data root, `~/.local/share/custom-openspec-workflow`, for the
installed package and Grill staging. Keep path calculation in shared path
helpers so the installer and Grill adapter cannot select different defaults.
The helpers must calculate the home directory at call time so tests can use a
temporary home directory.

The installer will use the data root as its Python search path. It will copy
the source package into the `custom_openspec_workflow` child directory. Its
wrapper modules will use the renamed import package.

### Rename configuration variables without aliases

Rename host variables to `CUSTOM_OPENSPEC_WORKFLOW_HOST`,
`CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR`, and
`CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR`. Rename the Grill staging variable to
`CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME`.

The explicit command options remain unchanged. An explicit option takes
precedence over its default. The old environment variables will not be read.

### Keep user-facing workflow names stable

Keep `custom-openspec-init`, `custom-openspec-grill`,
`custom-openspec-install`, and the `custom-openspec-grill` skill name. These
names are user-facing commands and capability names. They do not need to match
the Python import name.

### Test the installed shape

Add focused tests for the default data root, default Grill staging root,
renamed environment variables, copied package directory, wrapper import
targets, and explicit path overrides. Update existing imports and fixture
paths. Run the full test suite and the native OpenSpec validation after the
rename.

## Risks / Trade-offs

- Old imports or paths can remain after the rename. Search the repository for
  the old names and run packaging, unit, and integration checks.
- Package data can be excluded if the setuptools package-data key or resource
  lookup keeps the old package name. Test both source-tree resource access and
  the installed wrapper path.
- A wrapper can point to the new directory but import the old module name.
  Assert the generated wrapper text and run the installed helper in a
  disposable directory.
- Renaming environment variables can leave host discovery without a usable
  directory. Test each new variable and document the new names.

## Migration Plan

No migration plan is included. The project has no installed users. The new
names and paths apply to fresh installations. The installer will not inspect,
move, delete, or read old user data.
