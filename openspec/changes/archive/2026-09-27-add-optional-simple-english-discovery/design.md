# Design

## Context

See `proposal.md` for the motivation. The installer already creates an
`OperationPlan` before it writes user-level files. The plan stores structured
`PrerequisiteResult` values and sends them to human output, JSON output, dry
runs, and the programmatic install API. The result currently identifies a
feature and its remediation, but it does not state the value of an optional
skill.

The existing Grill integration discovers a skill by name in the selected Codex
skills directory. The new discovery follows the same host boundary. It checks
the standalone `simple-english/SKILL.md` file from `AminBlg/SimpleEnglish`.
It does not inspect the optional plugin, hook, or output-style files.

## Goals / Non-Goals

**Goals:**

- Report whether the selected skills directory contains `simple-english`.
- Use the existing structured prerequisite output in every install path.
- State the value of the optional `grill-me` and `simple-english` skills during installation.
- Keep the missing skill advisory and non-blocking.
- Keep the upstream skill outside package ownership and uninstall scope.
- Give users a stable source, skill path, and README reference for installation.
- Document the value of both skills in the README.
- Test available, missing, JSON, dry-run, and uninstall behavior.

**Non-Goals:**

- Do not copy, vendor, install, update, or modify the upstream skill.
- Do not install or inspect the upstream plugin, hook, or output style.
- Do not add Simple English rules to `openspec/config.yaml`.
- Do not add a Simple English adapter, staging flow, or compatibility command.
- Do not add a generic plugin or dependency-management framework.
- Do not change the OpenSpec schema, bootstrap flow, or package ownership manifest.

## Decisions

### Reuse the install-plan prerequisite path

Add the new result to the existing prerequisite collection. This keeps one
source of truth for human plans, JSON plans, dry runs, and final results. A
separate diagnostic command would duplicate the install path and could report
different state from the operation that follows.

The result will use the name `simple-english`, the skill kind, and a stable
documentation-writing feature label. It will include the selected skills
directory, the resolved `SKILL.md` path when the skill is available, and a
brief value statement.

### Store value separately from remediation

Add a `value` field to each known prerequisite result and serialize it with the
existing result fields. Human output will show the value beside the status.
JSON and dry-run output will expose the same value for scripts and users that
need the structured result.

Use these brief value statements:

- `grill-me`: surfaces unclear intent, hidden constraints, decisions,
  tradeoffs, non-goals, and open questions before planning.
- `simple-english`: helps write clear documentation with short sentences,
  active voice, and consistent terms.

Keep the value statement separate from remediation. Remediation tells the user
how to install a missing skill. An alternative is to put the value into the
feature label or remediation text, but that would hide it for available skills
and make structured output harder to consume.

### Share skill-name discovery logic

Move the small skill-name and host-root discovery behavior into a focused
internal helper. Keep `discover_grill_me_skill` as a compatibility wrapper and
add `discover_simple_english_skill` for the new check.

The helper will inspect the direct `<skills-dir>/<skill-name>/SKILL.md` path
first. It will also support the existing recursive fallback for installed
skill layouts. It will read front matter and accept a file only when its skill
name matches the requested name.

An alternative is to duplicate the Grill discovery code for Simple English.
That keeps the patch local, but it creates two copies of host and metadata
logic. A small internal helper removes that duplication without creating a
general dependency manager.

### Use one remediation message for Simple English

The remediation will name `AminBlg/SimpleEnglish`, `skills/simple-english`,
and the package README. It will not promise a host-specific plugin command.
The README can provide the upstream skill-only command, explain the value of
the skill in more detail, and explain that the package does not install the
dependency. The existing Grill remediation and README guidance will use the
same separation between value and installation steps.

### Keep the result additive and non-owning

The new item will use the existing `prerequisites` array. Missing status will
not add a conflict. The expected package files and ownership manifest will not
include the upstream skill. Uninstall will continue to build its plan from the
manifest and will not run prerequisite discovery.

### Record the upstream boundary without a version lock

Update the compatibility record with the repository, skill path, observed
skill version, and the small discovery contract. The package depends on the
Agent Skills file and skill name, not on the wording of the skill. It will not
pin or copy the upstream repository.

## Risks / Trade-offs

- A user can install Simple English in a nested supported skills layout. The
  recursive fallback preserves the existing Grill discovery behavior.
- A file can use the expected directory name but declare another skill name.
  Front matter matching prevents a false available result.
- The added JSON array item and `value` field can affect consumers that assume
  an exact item count or schema. The change keeps existing fields, adds only
  data, and updates tests to treat prerequisite names as a set.
- The upstream repository can change its skill metadata. The diagnostic will
  report the skill as missing when its name no longer matches and will direct
  the user to the current upstream README.
- Value text can drift from the detailed README text. The implementation will
  keep the brief statements in one source and test their presence in both
  install output and README assertions.
- A missing optional skill can look like an install failure. Human and JSON
  output will keep the result as a warning and will not add an install conflict.

## Migration Plan

No repository migration is required. After a package upgrade, users rerun the
installer or a dry run to receive the new result. Existing ownership manifests
remain valid because the upstream skill is not an owned file. Uninstall keeps
the existing manifest behavior and leaves Simple English untouched.
