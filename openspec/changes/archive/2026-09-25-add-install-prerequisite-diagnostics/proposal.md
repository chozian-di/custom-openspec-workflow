# Proposal

## Why

A prerequisite is a dependency that a feature needs to work. The installer
currently installs the custom Grill adapter without telling the user that the
upstream `grill-me` skill is missing. The user learns about the problem only
when a later Grill session fails.

The installer must report known missing prerequisites during the pre-write
plan. It must keep installation available because Grill is optional and normal
OpenSpec work does not need it.

## What Changes

- Add read-only prerequisite diagnostics to the install plan.
- Check the selected Codex skills directory for the upstream `grill-me` skill.
- Check whether the default `openspec` command is available on `PATH` for
  `custom-openspec-init`.
- Report missing feature prerequisites as non-blocking warnings.
- Show warnings in human output before confirmation and in dry-run output.
- Include structured prerequisite results in JSON plans and final JSON results.
- Preserve one valid JSON object on standard output for JSON results.
- Include the checked path, affected feature, status, and an installation hint
  for each missing prerequisite.
- Direct users to `satya-janghu/agent-skills`, the expected `skills/grill-me`
  path, and the relevant README instructions.
- Keep the upstream `grill-me` skill outside the package ownership manifest and
  uninstall scope.
- Keep runtime missing-dependency reporting in the custom Grill skill
  actionable and consistent with the installer warning.
- Add automated coverage for available and missing prerequisites, human output,
  JSON output, dry runs, confirmation behavior, and uninstall behavior.
- Update the README with a clear prerequisite section and setup guidance.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `custom-openspec-grill`: Add actionable guidance when the upstream `grill-me`
  skill is unavailable.
- `user-level-openspec-policy`: Add non-blocking prerequisite diagnostics to
  user-level installation and document their behavior.

## Impact

- `src/custom_openspec_workflow/install.py` will collect and report the
  prerequisite results while it builds an install plan.
- `src/custom_openspec_workflow/grill.py` and the custom Grill skill text may
  reuse existing dependency discovery and remediation wording.
- `tests/test_install.py`, `tests/test_grill.py`, and skill contract tests will
  cover the new reports without writing upstream or user-owned prerequisite
  files.
- `README.md` will document the upstream dependency, the `openspec` command
  requirement for repository bootstrap, and the non-blocking warning behavior.
- The ownership manifest, package file layout, uninstall behavior, OpenSpec
  schema, and upstream Grill Me implementation will remain unchanged.
