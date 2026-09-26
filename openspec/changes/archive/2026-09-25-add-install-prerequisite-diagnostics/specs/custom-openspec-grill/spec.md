# Spec Delta

## MODIFIED Requirements

### Requirement: Delegate requirements interrogation

`custom-openspec-grill` SHALL delegate the question process to the installed
upstream Grill Me skill from `satya-janghu/agent-skills`. It MUST NOT copy,
fork, or replace Grill Me interrogation logic, and it MUST perform no
implementation work.

When the upstream skill is unavailable, the adapter SHALL report the missing
dependency, the location that it checked, the upstream source location, and a
reference to the package README instructions. It MUST NOT install or modify
the upstream skill.

#### Scenario: Grill Me is available

- **WHEN** a user starts an OpenSpec Grill session
- **THEN** the adapter invokes the upstream Grill Me skill, allows its normal
  question process, and waits for its distilled result before producing
  OpenSpec context

#### Scenario: Grill Me is unavailable

- **WHEN** the adapter cannot find the configured upstream Grill Me skill
- **THEN** it reports the missing dependency, identifies the checked
  user-level skills location, directs the user to install `skills/grill-me`
  from `satya-janghu/agent-skills`, references the package README, performs
  no implementation work, and leaves existing Grill source material
  unchanged

#### Scenario: Grill is skipped

- **WHEN** a change is trivial or already sufficiently specified
- **THEN** the user can continue with normal OpenSpec Explore or Propose
  without running the adapter

