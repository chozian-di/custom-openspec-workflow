# Design

## Context

See `proposal.md` for the motivation. The installer already builds a complete
plan before it writes user-level files. It reports known prerequisites in that
plan, but its confirmation prompt does not call out the effect of a missing
OpenSpec command.

`custom-openspec-init` sends commands through `OpenSpecRunner`. It currently
discovers a missing executable only when the first subprocess call fails.
`custom-openspec-grill` already has a shared Grill Me installation hint and a
compatibility failure path. Its installed skill also tells the agent to report
the missing skill, but the messages do not use one clear contract.

The package must remain an add-on. It must not install OpenSpec or Grill Me,
change upstream files, or make OpenSpec a hard blocker for package
installation.

## Goals / Non-Goals

Goals:

- Make missing OpenSpec visible before package installation can write files.
- Use `--yes` as explicit acknowledgment for non-interactive installation.
- Give users one external OpenSpec installation path and a version check.
- Fail early and clearly when `custom-openspec-init` cannot run OpenSpec.
- Give the Grill wrapper the checked location and clear Grill Me installation
  guidance.
- Keep JSON output parseable and keep all prerequisite checks non-destructive.

Non-goals:

- Do not install, update, or remove OpenSpec.
- Do not install, update, or remove Grill Me.
- Do not make missing OpenSpec block installation of this package.
- Do not require Grill Me for Explore, Propose, or other normal OpenSpec work.
- Do not add a package manager dependency or network access to the installer.
- Do not change package ownership, manifest format, or uninstall scope.

## Decisions

### Use shared prerequisite guidance

Add a small prerequisite guidance module for the OpenSpec install command,
version check, and executable override text. The installer and bootstrap helper
will use the same guidance. Keep Grill Me guidance in the Grill adapter, with
the same checked-location and README facts in human, structured, and skill
output.

This avoids separate messages that tell users different setup steps. It also
keeps external installation outside the package code.

### Make the existing install confirmation acknowledge OpenSpec

Keep one confirmation step for a normal install. When OpenSpec is missing, the
human prompt will state that the workflow cannot function until OpenSpec is
installed and will ask whether to continue with package installation. The
human plan and JSON plan will show the same warning before the prompt.

`-y` and `--yes` will bypass the prompt and count as explicit acknowledgment.
Conflict checks will still refuse unsafe writes. A dry run will report the
warning without asking for acknowledgment because it writes nothing.

This preserves the current non-interactive contract and avoids two consecutive
prompts for one install operation.

### Preflight OpenSpec before bootstrap work

Check the selected executable before `custom-openspec-init` reads or changes
OpenSpec global configuration. For the default `openspec` value, check the
command on `PATH`. For an explicit executable value, check that selected path
or command instead.

If the check fails, return a clear error with the external install command, the
version check, and the explicit override. Do not create snapshots, call
OpenSpec, edit the target repository, or edit global configuration after this
failure.

### Keep Grill checks at the delegation boundary

The installed `custom-openspec-grill` skill will state that Grill cannot run
until `grill-me` is installed. The adapter's missing-dependency and
compatibility paths will report the checked skills directory, upstream source,
skill path, and README guidance.

Stage and attach operations do not need the upstream skill because they process
source and staged context. They will not gain an unrelated dependency check.
Normal OpenSpec work remains available when Grill Me is missing.

### Use the documented npm installation path

The README and missing-OpenSpec messages will use:

```text
npm install -g @fission-ai/openspec@latest
openspec --version
```

They will state that the project installer does not run these commands. They
will also show `--openspec-executable /path/to/openspec` for an executable that
is not on `PATH`.

## Risks / Trade-offs

- A user can pass `--yes` without reading the warning. The plan still contains
  the warning, and `--yes` is an explicit user instruction.
- OpenSpec can be installed outside `PATH`. The executable override and the
  bootstrap preflight provide a direct remedy.
- The `@latest` package can change over time. The version check lets the user
  confirm the installed command, while the compatibility baseline continues to
  record the version used by this package.
- A missing Grill Me skill stops only the Grill path. The wrapper must keep the
  optional-use message so users do not mistake this for a package failure.

## Migration Plan

No data migration is required. Users with an existing installation can rerun
the package installer to receive the updated helper and skill. Users must
install OpenSpec separately, then rerun `custom-openspec-init` or pass its
explicit executable path. Existing manifests, upstream skills, and staged
Grill sessions remain outside the change.
