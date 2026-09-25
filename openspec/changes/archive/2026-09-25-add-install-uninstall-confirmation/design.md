# Design

## Context

See proposal.md for the motivation and scope.

The current installer resolves a Codex skill directory, an executable directory,
and a package data root. It copies the Python package, copies the custom Grill
skill, and writes two wrappers. Its dry run returns locations, but it does not
list file operations or record ownership. It also replaces an existing copied
package directory before it copies the new content.

The installer is separate from `custom-openspec-init`. The installer changes
user-level files. `custom-openspec-init` changes a target repository and the
OpenSpec global workflow configuration. Uninstall must keep those operations
separate.

## Goals / Non-Goals

### Goals

- Add `--uninstall` to the existing `custom-openspec-install` command.
- Add `-y` and `--yes` for install and uninstall confirmation bypass.
- Use one complete plan for normal output, dry-run output, and JSON output.
- Require confirmation before writes in interactive use.
- Require `-y` or `--yes` when input is not interactive.
- Record package-owned paths and hashes in a manifest.
- Refuse unmanaged and user-modified conflicts before writes, including existing
  files without a trustworthy ownership manifest.
- Remove only unchanged package-owned user-level files during uninstall.
- Preserve Grill staging data and all repository-level changes.
- Keep the package free of new external dependencies.

### Non-Goals

- Do not remove or reverse `custom-openspec-init` changes.
- Do not remove the upstream `grill-me` skill.
- Do not remove unrelated files from the configured host directories.
- Do not add a `--force` option that overrides ownership checks.
- Do not migrate arbitrary old files when the installer cannot prove ownership.
- Do not change the OpenSpec schema, generated OpenSpec skills, or lifecycle.

## Decisions

### Keep one command with an uninstall flag

The command will keep its current install behavior and add
`custom-openspec-install --uninstall`. A separate executable or subcommand would
add another user-facing entry point without adding a safety benefit. The existing
path options will apply to both operations.

### Build one operation plan before any write

The installer will resolve all paths, inspect existing files, calculate the
expected install files, and build a plan before it changes anything. Each plan
entry will include an operation and an absolute target path. Install entries will
cover the copied package files, the custom skill, the two wrappers, the manifest,
and required parent directories. Uninstall entries will cover only managed files
and empty directories that the installer created.

The human output will show the plan before the confirmation question. For a JSON
operation that can write files, the command will write the complete plan to
standard error before the confirmation prompt or automatic apply. The final
operation result will be one JSON object on standard output. A JSON dry run will
return its plan in that result object because it does not write files. A
non-interactive command without `-y` or `--yes` will fail after planning and
before writing.

### Keep JSON plan ordering stable

Plan entries will use deterministic traversal order. The installer will scan
extra package and skill paths in sorted order. This keeps conflict entries stable
between JSON runs. Set-based traversal is not suitable because it can change
entry order between processes.

### Store ownership in a manifest

The manifest will live at the selected install root. It will record the install
root, the resolved skill and executable directories, the managed paths, their
installed content hashes, and the file modes needed for wrappers. The manifest
will be written only after all install files are ready.

During an upgrade, a managed path can change when its current content matches the
hash recorded by the previous install. When a trustworthy manifest exists, a path
that is not in the manifest, or a managed path that a user changed, is a
conflict. The installer will report all conflicts during planning and stop before
any write.

If existing package files, the custom skill, wrappers, or extra files under the
package or custom skill directories have no trustworthy manifest, the installer
will report an unmanaged conflict. It will not claim ownership from a path name
or matching content. An empty target is valid for a fresh install and receives a
new manifest. Uninstall without a trustworthy manifest refuses to guess.

### Preserve modified files during uninstall

Uninstall will compare each managed file with its recorded hash. It will remove
only files that still match. It will preserve changed files and report them as
uninstalled files that need user review. It will remove an empty parent directory
only when the installer created that directory and no unrelated file remains.

The uninstall operation will never remove the install root itself. In particular,
it will leave the sibling `grill` staging directory and its sessions in place.

### Apply changes as a guarded operation

The installer will complete path validation and conflict detection before it
writes. It will stage copied files and wrapper content in temporary paths, use
atomic replacement for individual files, and keep the previous managed state
available while an operation is in progress. If an install or uninstall fails,
it will restore the prior managed state where possible and will not publish a new
manifest for a partial install.

### Keep repository cleanup out of the command

The command will document that user-level uninstall is not a reverse bootstrap.
It will not scan repositories, edit `openspec/config.yaml`, edit `.agents`, or
change OpenSpec global configuration. Users who need to remove policy from a
repository must make that repository change separately.

## Risks / Trade-offs

- An existing installation without a trustworthy manifest cannot be upgraded or
  uninstalled automatically. The installer refuses uncertain paths and requires
  manual cleanup.
- A user modification to a managed wrapper or skill can leave that file after
  uninstall. The result reports the path instead of deleting user data.
- A failure during a multi-file operation can leave temporary files. Staging,
  atomic replacement, and restoration reduce this risk, and the manifest is
  committed only after a complete install.
- Requiring confirmation changes unattended installs. The `-y` and `--yes`
  options provide an explicit automation path, and non-interactive failures
  occur before writes.
- Absolute host paths in the manifest can become stale after a user moves a
  directory. The command reports the recorded paths and requires an explicit
  path selection to operate on a different location.

## Migration Plan

1. Add the plan, confirmation, manifest, conflict, install, and uninstall code.
2. Preserve the existing explicit path options and add `--uninstall`, `-y`, and
   `--yes`.
3. Run the installer in disposable directories to create a new manifest.
4. Test repeated install, upgrade, cancellation, conflict refusal, and uninstall.
5. Document that existing installations without a trustworthy manifest cannot be
   upgraded or removed automatically.

## Open Questions

None. The command scope, confirmation behavior, ownership policy, and repository
boundary were decided during exploration.
