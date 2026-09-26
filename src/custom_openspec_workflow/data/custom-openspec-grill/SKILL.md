---
name: custom-openspec-grill
description: Use the installed upstream Grill Me skill to prepare traceable supplemental context for an OpenSpec change. Use for ambiguous or substantial changes when deeper requirements discovery helps. Skip for trivial or already-specified changes.
compatibility: codex
---

# Custom OpenSpec Grill

This skill is a thin adapter. It does not contain a question process and it
does not implement project changes.

## Delegate to Grill Me

The adapter checks the selected Codex user-level skills directory. The default
directory is `~/.agents/skills`. It looks for the upstream skill at
`grill-me/SKILL.md`.

1. Find the installed upstream skill named `grill-me` in the selected user-level skills directory.
2. If `grill-me/SKILL.md` is missing, report the checked directory.
3. Tell the user to install `skills/grill-me` from `satya-janghu/agent-skills`.
4. Refer to the package README. Stop and leave existing Grill source material unchanged.
5. Delegate the requirements session to the upstream `grill-me` skill by using the host skill invocation for `grill-me`.
6. Wait for the upstream skill to return its distilled result. Do not ask a second set of questions in this adapter.

The upstream skill owns the questions and the session log. This adapter does
not copy its prompts, question lenses, logging rules, or interrogation logic.

## Stage or attach the result

If no named OpenSpec change exists, retain the upstream source in its normal
`.grill` location and stage it outside the repository with:

```text
custom-openspec-grill stage --source .grill/<source-file>.md
```

The command reports a stable session identity. Use that identity later. Do not
create a root-level `grill.md` before a named change exists.

If a named change exists, attach the staged session with:

```text
custom-openspec-grill attach --change <change-name> --session <session-id>
```

The command writes supplemental `grill.md` inside the named change. It keeps
the source identity and source traceability. It does not add `grill.md` to the
OpenSpec schema.

If the change already has `grill.md`, stop and ask the user whether to replace
or combine the existing context. A repeated attachment of the same session is
already complete.

## Required context

The attached file keeps these sections:

- Intent.
- Constraints.
- Decisions.
- Assumptions Surfaced.
- Open Questions.
- Non-Goals or Out of Scope.

Resolved decisions stay in Decisions. Unresolved items stay in Open Questions.
Proposal, specification, design, task, Apply, Verify, and Archive work treats
the file as supplemental planning input. Normal OpenSpec artifacts and
commands remain authoritative.

Skip this skill when normal Explore or Propose already has enough information.
