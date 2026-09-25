# Proposal

## Why

The user-level installer currently replaces package files and helper paths without
asking for confirmation. It also has no supported uninstall operation, so users
cannot remove the installed package with the same level of safety and visibility.

## What Changes

- Add a complete pre-write plan for installation. The plan lists each user-level
  file that the operation will create, replace, or remove.
- Ask for confirmation before install and uninstall operations when the user does
  not pass `-y` or `--yes`.
- Add `-y` and `--yes` aliases that bypass the confirmation prompt but do not
  bypass ownership or conflict checks.
- Add `--uninstall` to `custom-openspec-install`.
- Add a manifest with file hashes for package-owned user-level files.
- Refuse unmanaged or modified file conflicts before installation writes files.
- Remove unchanged managed files during uninstall and preserve modified files
  with a report.
- Keep repository files, OpenSpec configuration, OpenSpec global configuration,
  and Grill staging sessions outside uninstall scope.
- Make `--dry-run` show the same file-level plan without writing files.
- Make JSON mode show the complete plan before confirmation or automatic apply
  while keeping the final result machine-readable.
- Document installation confirmation, non-interactive use, uninstall scope,
  conflict handling, and upgrade behavior.
- Add tests for planning, confirmation, ownership, conflict refusal, uninstall,
  and preservation of unrelated files.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-level-openspec-policy`: Define safe, confirmable installation and
  uninstall behavior for the user-level package.

## Impact

- `src/custom_openspec_workflow/install.py` will gain planning, confirmation,
  manifest, install, and uninstall behavior.
- `tests/test_install.py` will cover the new command and file ownership rules.
- `README.md` will document the new commands and safety behavior.
- The package will add a small user-level manifest at the selected install root.
- `custom-openspec-init` and its repository-level changes will not be removed by
  this change.
