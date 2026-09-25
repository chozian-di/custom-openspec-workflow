# Design

## Context

See `proposal.md` for the motivation.

`paths.py` currently defines the persistent data root under
`~/.local/share/custom-openspec-workflow`. `install.py` copies the Python
package there and generates Python wrappers that insert that directory into
`sys.path` before importing a command module. The repository launchers are
POSIX shell scripts that run the same command modules from the source tree.

Python reads `PYTHONPYCACHEPREFIX` when the interpreter starts. Setting only
`os.environ["PYTHONPYCACHEPREFIX"]` after startup does not change the active
cache prefix. Python 3.10 or newer is already required by the project.

## Goals / Non-Goals

Goals:

- Keep persistent package files under the existing data root.
- Use `~/.cache/custom-openspec-workflow` as the default bytecode cache root.
- Set the cache prefix before package imports for installed and repository
  launchers.
- Preserve a user-provided `PYTHONPYCACHEPREFIX` value.
- Keep cache files outside the installer manifest and uninstall file scope.
- Test the behavior at the process boundary in disposable directories.

Non-Goals:

- Do not move the installed Python package into the cache directory.
- Do not add a new project-specific cache environment variable.
- Do not change the OpenSpec schema or generated OpenSpec skills.
- Do not migrate or remove old package-local `__pycache__` directories.
- Do not make the package initializer change the cache prefix for unrelated
  Python imports in the same process.

## Decisions

### Add a shared default cache path

Add `default_cache_root()` beside `default_data_root()` in `paths.py`. It will
return `Path.home() / ".cache" / "custom-openspec-workflow"` at call time.
The installer will use this value when it creates wrapper content. Tests can
therefore select a disposable home directory without changing process-global
state.

The standard `PYTHONPYCACHEPREFIX` variable remains the only cache override.
The default path stays exact and does not add an `XDG_CACHE_HOME` policy that
the project does not use for its existing data path.

### Generate launchers that set the prefix before Python starts

Change generated helper wrappers from direct Python scripts to POSIX shell
launchers. Each launcher will:

1. Select the existing `PYTHONPYCACHEPREFIX` value when it is set.
2. Otherwise select the installed default cache root.
3. Export the selected value.
4. Start Python and pass the installed data root as an argument.
5. Insert that data root at the front of `sys.path` before importing the
   command module.

The last two steps preserve the current behavior where the installed package
takes precedence over a package with the same name in the current directory.
The launcher will call the existing module `main` function and will pass the
original command arguments unchanged.

Update the repository shell launchers with the same environment assignment
before their existing `python3 -m` calls. This keeps source-tree execution and
installed execution aligned.

### Keep cache data outside installer ownership

The manifest will continue to list only package files, the custom skill,
wrappers, and the manifest-owned directories. Python creates cache directories
when a helper runs, so the installer will not try to predict or hash them.
Uninstall will leave the cache root and its contents unchanged.

`PYTHONPYCACHEPREFIX` uses a parallel path for absolute source paths. The
cache can therefore contain bytecode for the standard library and runtime
dependencies as well as this package. This is expected behavior for the
Python cache prefix.

### Test the installed process boundary

Add tests for these behaviors:

- The default cache path follows the current home directory at call time.
- Generated wrappers contain the cache setup and the renamed command module.
- A disposable installed helper creates no `.pyc` file below the installed
  package directory when the default prefix is active.
- The same helper creates bytecode below the selected cache root.
- An explicit `PYTHONPYCACHEPREFIX` value takes precedence over the default.
- Repository shell launchers set the default before importing package modules.
- The manifest does not claim cache files, and uninstall does not remove them.

## Risks / Trade-offs

- [Risk] The cache prefix stores bytecode for imported dependencies too.
  -> Document this behavior and keep the cache outside persistent package and
  manifest paths.
- [Risk] Generated wrappers become POSIX shell launchers instead of Python
  scripts.
  -> The supported environment already uses POSIX shell launchers, and tests
  will execute both generated helpers.
- [Risk] A user-provided cache prefix can point outside the project cache
  root.
  -> Preserve the standard Python override and document the default value.
- [Risk] An old package-local cache can remain after an upgrade.
  -> The project is unreleased and has no installed users. Do not add migration
  behavior to this change.

## Migration Plan

No migration is required. Fresh installations will generate the new launcher
content. The existing ownership manifest will update wrapper hashes during a
future install, while the bytecode cache remains outside the manifest.

Rollback consists of reverting the launcher and path changes. Rollback does
not remove any cache directory or cache file.
