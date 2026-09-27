# Proposal

## Why

The installer reports the upstream `grill-me` skill and the `openspec` command,
but it does not report the optional `simple-english` skill. Users cannot see
whether the selected Codex skills directory contains this documentation aid.
The install result also does not explain the value of the optional skills.
The package needs advisory visibility and short value statements without
making either skill a required part of installation or OpenSpec work.

## What Changes

- Discover `simple-english/SKILL.md` in the selected Codex user-level skills directory.
- Add its status, checked location, resolved path, and remediation to the install plan.
- Add a brief value statement for the optional `grill-me` and `simple-english` skills.
- Show the result in human-readable plans, JSON plans, final JSON results, and dry runs.
- Keep a missing Simple English skill non-blocking for installation.
- Direct users to `AminBlg/SimpleEnglish`, the `skills/simple-english` path, and the package README.
- Add tests and a fixture for available and missing Simple English discovery.
- Update the README and the existing prerequisite specification.
- Add detailed README descriptions of the value that Grill Me and Simple English provide.
- Record the upstream repository, skill path, observed version, and discovery contract in the compatibility baseline.
- Keep the upstream skill outside package ownership, installation, upgrade, and uninstall behavior.
- Do not add policy rules that require Simple English or install its optional plugin features.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-level-openspec-policy`: add the optional Simple English skill to the known install-plan diagnostics while preserving non-blocking and non-owning behavior.

## Impact

The installer will gain one skill discovery result and value statements in its
existing prerequisite collection. Its JSON output will gain one additional
item and a `value` field in the existing `prerequisites` results. The package
will add discovery and remediation logic, test coverage, a fixture, README
guidance, and compatibility evidence. The ownership manifest, package file
set, uninstall scope, OpenSpec schema, bootstrap behavior, and upstream
Simple English files will remain unchanged.
