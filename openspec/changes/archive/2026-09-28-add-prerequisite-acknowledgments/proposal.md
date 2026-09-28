# Proposal

## Why

The installer currently reports a missing OpenSpec executable as an advisory
warning, but the warning does not clearly tell the user that this workflow
cannot function until OpenSpec is installed. The bootstrap helper and Grill
wrapper also need consistent, actionable messages when their upstream
dependencies are unavailable.

## What Changes

- Keep a missing OpenSpec executable non-blocking for installation of this
  package.
- Add a clear OpenSpec warning and acknowledgment prompt before an interactive
  install writes files.
- Treat `-y` and `--yes` as explicit acknowledgment for non-interactive
  installation.
- Explain how to install OpenSpec without having this installer install it,
  including verification and an explicit executable-path override.
- Add an early, clear missing-OpenSpec message to `custom-openspec-init` before
  it performs repository or global configuration work.
- Make the `custom-openspec-grill` wrapper report the checked location and
  actionable installation guidance when `grill-me` is missing, while keeping
  Grill optional for the wider OpenSpec workflow.
- Keep missing prerequisite handling non-destructive and leave upstream
  dependencies outside package ownership and uninstall scope.
- Add tests for acknowledgment, `--yes`, cancellation, JSON and dry-run
  output, bootstrap preflight failure, and missing Grill Me guidance.
- Update the README and affected OpenSpec requirements with the new behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-level-openspec-policy`: Require clear acknowledgment of missing
  OpenSpec during package installation and document external installation
  guidance.
- `custom-openspec-init`: Report missing OpenSpec before bootstrap work with
  actionable installation and executable-override guidance.
- `custom-openspec-grill`: Report a missing `grill-me` dependency consistently
  without installing or modifying the upstream skill.

## Impact

- Update `src/custom_openspec_workflow/install.py` to format the OpenSpec
  warning and integrate it with the existing confirmation and JSON paths.
- Update `src/custom_openspec_workflow/bootstrap.py` to preflight the selected
  OpenSpec executable before repository or global changes begin.
- Align `src/custom_openspec_workflow/grill.py`, the Grill CLI, and the
  installed custom Grill skill around missing-dependency guidance.
- Extend installer, bootstrap, Grill, skill-contract, and README tests.
- Update `README.md` and delta specifications.
- Do not add an OpenSpec package dependency, invoke a package manager, modify
  upstream OpenSpec or Grill Me files, or make missing OpenSpec a package
  installation blocker.
