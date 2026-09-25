# Spec Delta

## ADDED Requirements

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
