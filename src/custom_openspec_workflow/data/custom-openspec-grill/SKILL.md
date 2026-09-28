---
name: custom-openspec-grill
description: Use the installed upstream Grill Me skill to prepare traceable supplemental context for an OpenSpec change. Use for ambiguous or substantial changes when deeper requirements discovery helps. Skip for trivial or already-specified changes.
compatibility: codex
---

# Custom OpenSpec Grill

The official package name is `custom-openspec-workflow`. Its short name is
`COW`, and it is also known as "chozian's OpenSpec Workflow".

This skill coordinates the upstream `grill-me` skill with OpenSpec planning.
It does not contain a question process and it does not implement project code.
It does not implement project changes.

## Protect the `.grill/` directory

Before you invoke Grill Me or use a source under a repository's `.grill/`
directory, identify the target repository and run:

```text
git -C <repository> check-ignore -q -- .grill/
```

If the command does not confirm that `.grill/` is ignored, stop. Do not edit `.gitignore`.
Tell the user to add `.grill/` to `<repository>/.gitignore`, then run the
workflow again. Do not invoke Grill Me, stage a source, or attach a session
while this preflight fails.

After the preflight succeeds, treat every source under `.grill/` as a
read-only snapshot. Do not edit or delete the source during the workflow.

## Delegate to Grill Me

The adapter checks the selected Codex user-level skills directory. The default
directory is `~/.agents/skills`. It looks for the upstream skill at
`grill-me/SKILL.md`.

1. Find the installed upstream skill named `grill-me` in the selected user-level skills directory.
2. If `grill-me/SKILL.md` is missing, report the checked directory.
3. State that Grill cannot run until `grill-me` is installed.
4. Tell the user to install `skills/grill-me` from `satya-janghu/agent-skills`.
5. Tell the user to read the package README for host-specific instructions.
6. State that normal OpenSpec Explore and Propose work remains available.
7. Stop and leave existing Grill source material unchanged.
8. Delegate the requirements session to the upstream `grill-me` skill by using the host skill invocation for `grill-me`.
9. Wait for the upstream skill to return its distilled result. Do not ask a second set of questions in this adapter.

The upstream skill owns the questions and the session log. This adapter does
not copy its prompts, question lenses, logging rules, or interrogation logic.

## Select and stage the source

After the upstream session returns, use the exact source path in its result.
Do not reconstruct a path from a generated filename slug. Do not choose a
source only because it has the newest timestamp.

If the result has no exact source path, inspect plausible source files only
when exactly one plausible source exists. If more than one plausible source
exists, ask the user to select the source. Do not stage a source before the
user selects it. If no plausible source exists, ask the user to provide the
source path.

After source selection, run the existing adapter through the AI session:

```text
custom-openspec-grill stage \
  --source <exact-source-path> \
  --json
```

Read the JSON result. Record this pending handoff in the active AI session:

- The target repository root.
- The exact `sourcePath`.
- The returned `sessionId`.
- The returned `stagingDir`.

Keep the pending handoff until the session attaches to a named change or the
user chooses not to continue. Do not ask the user to repeat the source path or
session identity while the handoff is available.

## Attach the pending session

When a named OpenSpec change exists, attach the pending session before the
next planning artifact that uses Grill context. In the recommended Propose
flow, attach after Propose creates the named change and before Propose writes
`proposal.md` or another initial planning artifact.

Use the repository root and the exact returned session identity:

```text
custom-openspec-grill attach \
  --root <repository> \
  --change <change-name> \
  --session <session-id> \
  --json
```

If exactly one applicable named change exists, select it automatically. If
more than one applicable named change exists, ask the user to select the
change. Do not attach to an arbitrary change.

If the selected change already has `grill.md` for another session, preserve
the existing context and ask the user whether to replace or combine it.
Do not pass `--replace` or `--combine` without explicit user choice.
A repeated attachment of the same session is already complete.

The source under `.grill/` and the change-local `grill.md` are read-only
snapshots after capture or attachment. Do not edit or delete either file.
Record later decisions in the normal OpenSpec artifacts.
The latest explicit user decision takes precedence over a summary or snapshot.

## Recommended planning order

Use this order for a normal change:

1. Use OpenSpec Explore for discussion and repository investigation.
2. If important requirements remain unresolved, run this skill. Grill Me is optional.
3. Use OpenSpec Propose as the normal writer of the initial planning artifacts.
4. After Propose creates the named change, attach the pending session before the initial artifacts are written.
5. Continue with normal OpenSpec planning and implementation.

If Explore provides enough clarity, continue to Propose without Grill Me. Keep
the pending handoff when Grill Me runs before Propose. Grill-first remains
available for a change with high uncertainty. In that case, run Grill Me,
retain the handoff, use Explore to test the captured decisions against the
repository, and then use Propose.

OpenSpec 1.13.2 does not provide a supported Explore guidance field. This
package cannot block native Explore from creating or updating planning
artifacts after the user explicitly confirms those writes. If Explore writes
an artifact before Grill runs, preserve it and do not claim that it used Grill
context. Do not rewrite that artifact automatically after attachment.
The user can use OpenSpec Update to reconcile it with the attached context.

## Required context

The attached file keeps these sections:

- Intent.
- Constraints.
- Decisions.
- Assumptions Surfaced.
- Open Questions.
- Non-Goals or Out of Scope.

Resolved decisions stay in Decisions. Unresolved items stay in Open Questions.
The attached file is supplemental planning context. It is not a schema
artifact. Skip this skill when normal Explore or Propose already has enough information.
