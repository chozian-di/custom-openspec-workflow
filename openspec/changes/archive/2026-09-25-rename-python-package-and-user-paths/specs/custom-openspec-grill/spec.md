# Spec Delta

## MODIFIED Requirements

### Requirement: Stage Grill results before a change exists

When no OpenSpec change exists, the adapter SHALL retain the Grill source
material in a non-root staging location and assign or preserve a stable session
identity. It MUST NOT create an unrelated root-level `grill.md` or a custom
OpenSpec schema artifact. When the user does not provide an explicit staging
directory, the adapter SHALL use
`~/.local/share/custom-openspec-workflow/grill/` unless
`CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME` provides another location.

#### Scenario: User grills before proposal creation

- **WHEN** the user runs the adapter before an OpenSpec change exists
- **THEN** the adapter retains the source in the documented non-root staging area and reports a stable identity that can be attached to a later named change

#### Scenario: The default staging location is used

- **WHEN** the user stages a source without an explicit staging directory or environment override
- **THEN** the adapter stores the session under `~/.local/share/custom-openspec-workflow/grill/sessions/<session-id>/`

#### Scenario: The user selects a staging location

- **WHEN** the user provides `--staging-dir` or sets `CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME`
- **THEN** the adapter uses the selected location instead of the default staging location

#### Scenario: Grill source uses a generated slug

- **WHEN** the upstream source is named with a generated filename slug
- **THEN** later attachment uses the stable session identity and source traceability instead of relying only on that slug
