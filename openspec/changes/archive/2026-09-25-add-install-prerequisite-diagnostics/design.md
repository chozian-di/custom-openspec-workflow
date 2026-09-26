# Design

## Context

See `proposal.md` for the motivation. The installer already builds an
`OperationPlan` before it asks for confirmation or writes user-level files.
The plan already feeds human output, JSON output, dry runs, and the programmatic
install API.

The Grill adapter already discovers `grill-me` by skill name and reads the
selected skills directory. The host module already provides executable lookup.
The custom Grill skill and the README already state that Grill Me is an
upstream prerequisite.

## Goals / Non-Goals

Goals:

- Add small, read-only checks to the existing install plan.
- Report both the checked location and the feature that uses each prerequisite.
- Keep missing feature prerequisites separate from file conflicts.
- Keep human and JSON output consistent across install, dry run, and
  confirmation paths.
- Give users enough information to install `grill-me` without guessing the
  upstream source or skill path.
- Keep the upstream skill outside package ownership and uninstall behavior.

Non-goals:

- Do not download, install, update, or modify `grill-me`.
- Do not add a generic plugin or dependency-management framework.
- Do not make missing feature prerequisites block package installation.
- Do not change the OpenSpec schema or the repository bootstrap workflow.
- Do not add prerequisite checks to uninstall.

## Decisions

### Store prerequisite results on the install plan

Add a structured prerequisite result collection to `OperationPlan`. Each result
will contain a stable name, feature, kind, status, checked location, and
remediation text. The plan serializer will include this collection in both
dry-run and write-mode payloads.

This keeps one source of truth for the human plan, JSON plan, final result, and
programmatic API. A separate diagnostic command would duplicate the plan path
and could report a different result from the operation that follows.

### Check the selected skills directory directly

Pass the resolved `skills_dir` from the install layout to the existing
`grill-me` discovery function. Do not call default host discovery for this
check.

The installer can receive explicit skills and binary directories. Host
discovery also checks for a writable binary directory, so using it for the
skill check could hide the real Grill result behind an unrelated host error.
The selected install location is the location the user needs to fix.

### Check the default OpenSpec command on PATH

Use the existing executable lookup for `openspec`. Report its resolved path
when it is available. Report that `custom-openspec-init` needs an OpenSpec
executable when it is missing.

This check is advisory because the bootstrap helper accepts an explicit
`--openspec-executable` value. The installer does not need to predict that
override.

### Keep missing results non-blocking

Missing `grill-me` and `openspec` results will not set the install plan as
blocked. Existing path, manifest, and ownership conflicts will keep their
current blocking behavior.

This separates package installation from optional or later feature setup. It
also lets a user install the package before installing OpenSpec or Grill Me.

### Show warnings through existing output paths

The human plan printer will show prerequisite warnings after the file entries
and before the confirmation prompt. The JSON plan serializer will include the
same structured data on standard error before confirmation or apply. The final
JSON result will include the same data on standard output.

The installer will not print extra unstructured text to JSON standard output.
This preserves the current contract for scripts that parse the final result.

### Use one remediation message for Grill Me

The installer warning, the custom Grill skill, and the compatibility failure
will use the same facts:

- The missing skill is `grill-me`.
- The expected upstream source is `satya-janghu/agent-skills`.
- The upstream skill path is `skills/grill-me`.
- The package README contains the detailed setup instructions.

The message will also identify the path that the check inspected. The package
will not promise one host-specific download command because host installation
methods can differ.

### Leave uninstall and ownership unchanged

Prerequisite checks will run only while building install plans. The manifest
will continue to contain only package-owned files. Uninstall will not inspect,
remove, or report on the upstream `grill-me` skill.

## Risks / Trade-offs

Risk: A user has OpenSpec installed outside `PATH`.

Mitigation: Report the missing default command as advisory and state that
`custom-openspec-init` accepts an explicit executable override.

Risk: A custom skills directory is empty before the first install.

Mitigation: Check the resolved target path before installation and report the
missing upstream skill without treating the empty directory as a conflict.

Risk: A JSON consumer rejects a new top-level field.

Mitigation: Keep the existing fields and JSON object shape intact. Add only a
new structured field and test both the pre-apply plan and final result.

Risk: The warning suggests that all `custom-openspec-grill` commands need the
upstream skill.

Mitigation: State that the prerequisite is needed for Grill sessions. Keep
staging and attachment behavior unchanged.

Risk: Upstream Grill Me changes its installation layout.

Mitigation: Keep discovery based on the installed skill name and preserve the
existing compatibility check. Keep the remediation source and skill path in
the README so the setup guidance can change independently.

## Migration Plan

No migration is required. Existing manifests and installed files remain valid.
Users receive the new diagnostics after they install or upgrade the package.
The upstream `grill-me` skill remains user-owned and outside the package
upgrade and uninstall operations.

