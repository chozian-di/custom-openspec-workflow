# Spec Delta

## MODIFIED Requirements

### Requirement: Report known installation prerequisites

The user-level installer SHALL perform read-only prerequisite checks while it
builds an install plan. A prerequisite is a dependency that a package feature
needs or can use.

For an install operation, the checks SHALL include:

- The selected Codex user-level skills directory for the upstream `grill-me`
  skill.
- The selected Codex user-level skills directory for the optional upstream
  `simple-english` skill.
- The default `openspec` command on `PATH` for repository bootstrap.

Each result SHALL identify the prerequisite, the feature that uses it, its
status, the location or command that was checked, and an actionable
remediation when it is missing. Results for optional skill dependencies SHALL
also include a brief statement of the value that the skill provides. The
installer MUST NOT treat a missing feature prerequisite as a file ownership
conflict.

#### Scenario: Grill Me is missing

- **WHEN** the selected skills directory does not contain the upstream `grill-me`
  skill
- **THEN** the install plan states that Grill Me surfaces unclear intent,
  hidden constraints, decisions, tradeoffs, non-goals, and open questions
  before planning, identifies the checked location, and directs the user to
  install `skills/grill-me` from `satya-janghu/agent-skills` using the package
  README instructions

#### Scenario: Grill Me is available

- **WHEN** the selected skills directory contains the upstream `grill-me` skill
- **THEN** the install plan reports the prerequisite as available, states that
  Grill Me surfaces unclear intent, hidden constraints, decisions, tradeoffs,
  non-goals, and open questions before planning, and does not claim ownership
  of or plan changes to that skill

#### Scenario: Simple English is missing

- **WHEN** the selected skills directory does not contain the upstream
  `simple-english` skill
- **THEN** the install plan reports that the optional documentation aid is
  unavailable, states that Simple English helps write clear documentation
  with short sentences, active voice, and consistent terms, identifies the
  checked location, and directs the user to install `skills/simple-english`
  from `AminBlg/SimpleEnglish` using the package README instructions

#### Scenario: Simple English is available

- **WHEN** the selected skills directory contains the upstream
  `simple-english` skill
- **THEN** the install plan reports the skill as available, states that Simple
  English helps write clear documentation with short sentences, active voice,
  and consistent terms, and does not claim ownership of or plan changes to
  that skill

#### Scenario: OpenSpec is missing from PATH

- **WHEN** the default `openspec` command is not available on `PATH`
- **THEN** the install plan reports that `custom-openspec-init` needs an
  OpenSpec executable, identifies that the default command was not found, and
  tells the user that the helper supports an explicit executable override

#### Scenario: A missing feature prerequisite does not block installation

- **WHEN** one or more known feature prerequisites are missing and no file
  conflict exists
- **THEN** the installer displays the warnings and continues with normal
  confirmation and install behavior

### Requirement: Preserve prerequisite diagnostics across installer output

The installer SHALL include prerequisite results in the human-readable plan,
the dry-run result, and the JSON plan and final result. Human-readable output
SHALL show missing prerequisite warnings before confirmation. JSON output SHALL
keep the plan on standard error before confirmation or apply and SHALL keep one
valid final result object on standard output.

Prerequisite diagnostics SHALL run for install and dry-run operations. They
MUST NOT run as a condition for uninstall, change the ownership manifest, or
remove upstream skills or other user-owned files.

Human-readable and structured install output SHALL show the value statement
for `grill-me` and `simple-english` whether each skill is available or missing.

#### Scenario: Human install plan reports a missing prerequisite

- **WHEN** a user runs an install without `--yes` and a known prerequisite is
  missing
- **THEN** the plan displays the warning and the optional skill's value
  statement before the confirmation prompt, and the user can cancel without
  any user-level file change

#### Scenario: JSON install reports a missing prerequisite

- **WHEN** a user runs an install with `--json` and a known prerequisite is
  missing
- **THEN** the pre-apply plan and final result contain structured prerequisite
  data with the optional skill's value statement, and standard output remains
  one parseable JSON object for the final result

#### Scenario: Dry run reports a missing prerequisite without writing

- **WHEN** a user runs an install with `--dry-run` and a known prerequisite is
  missing
- **THEN** the result reports the warning and value statement, and the
  installer changes no user-level path

#### Scenario: Uninstall does not depend on feature prerequisites

- **WHEN** a user uninstalls the package while `grill-me`, `simple-english`, or
  `openspec` is unavailable
- **THEN** uninstall follows its existing manifest and conflict rules without
  blocking on prerequisite diagnostics and without changing upstream files
