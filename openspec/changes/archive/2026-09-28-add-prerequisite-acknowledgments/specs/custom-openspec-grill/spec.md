# Spec Delta

## ADDED Requirements

### Requirement: Explain a missing Grill Me dependency

When the `custom-openspec-grill` wrapper cannot find the upstream `grill-me`
skill, it SHALL report the checked user-level skills directory and state that
Grill cannot run until the skill is installed. The message SHALL direct the
user to install `skills/grill-me` from `satya-janghu/agent-skills` and read the
package README for host-specific instructions.

The wrapper SHALL stop the Grill operation without installing or changing the
upstream skill or existing Grill source material. Missing Grill Me SHALL not
prevent normal OpenSpec Explore or Propose work.

#### Scenario: Grill Me is missing

- **WHEN** a user starts the Grill wrapper and `grill-me/SKILL.md` is not in
  the selected skills directory
- **THEN** the wrapper reports the checked directory, the missing dependency,
  the installation source and path, and the README reference, then stops
  without changing source material

#### Scenario: Grill Me is available

- **WHEN** the selected skills directory contains the upstream `grill-me`
  skill
- **THEN** the wrapper continues with normal delegation and does not report a
  missing dependency

#### Scenario: Grill is skipped

- **WHEN** the user continues with normal OpenSpec work without Grill
- **THEN** missing Grill Me does not block Explore or Propose
