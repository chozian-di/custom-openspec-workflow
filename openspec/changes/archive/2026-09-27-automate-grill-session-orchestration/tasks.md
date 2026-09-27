# Tasks

## 1. Agent-managed Grill orchestration

- [x] 1.1 Update `src/custom_openspec_workflow/data/custom-openspec-grill/SKILL.md` so the agent checks that `.grill/` is ignored before it invokes Grill Me or stages a source. Require the agent to stop with instructions when the directory is not ignored and never edit `.gitignore`. Verify the skill describes this preflight and the read-only source rule.
- [x] 1.2 Update the packaged skill so the agent uses the upstream result's exact source path, uses one-source fallback discovery only when safe, asks about multiple sources, runs `stage --source <source> --json`, and records the pending handoff. Verify the skill contains the required execution order and does not copy upstream question logic.
- [x] 1.3 Document the recommended planning order in the packaged skill: Explore discussion, optional Grill Me, then Propose as the normal initial artifact writer. Keep Grill-first available for high-uncertainty changes. Require attachment after Propose creates the named change and before initial artifacts are written. State that native Explore artifact writes cannot be blocked by this package and that prior artifacts are not rewritten automatically. Verify the skill states these limits and the read-only snapshot rule.
- [x] 1.4 Extend `tests/test_skill_contract.py` for the ignore preflight, exact-source preference, source ambiguity, change ambiguity, session retention, automatic staging, attachment before Propose artifacts, the recommended Explore-first order, the Grill-first alternative, the native Explore write limitation, the no-rewrite rule, latest explicit decision precedence, conflict safeguards, and unchanged upstream question process. Verify the focused skill contract test passes.

## 2. Policy and user documentation

- [x] 2.1 Update `src/custom_openspec_workflow/data/openspec-policy.yaml` so proposal, specification, design, and task guidance completes a pending Grill attachment before a normal artifact uses Grill context. State that Grill context is supplemental, the latest explicit user decision takes precedence, and the policy cannot enforce Explore's no-write convention. Do not add unsupported Explore guidance. Verify the policy parses as YAML and preserves the existing Apply and Archive rules.
- [x] 2.2 Update the Grill sections in `README.md` to make Explore discussion, optional Grill Me, and Propose the normal path. Document Grill-first for high-uncertainty changes, the native Explore write limitation, source and change ambiguity prompts, the pending handoff, read-only snapshots, latest-decision precedence, native Archive paths, manual retention, recovery commands, and the installer step needed to deploy the updated skill. Verify the documented commands match the packaged skill and the README contract checks pass.

## 3. Package and workflow validation

- [x] 3.1 Confirm that the existing adapter tests cover stable session identity, external staging, source traceability, unchanged source material, repeated attachment, and existing-context protection. Add focused adapter coverage only if a changed contract is not already covered. Verify the focused Grill and validation tests pass.
- [x] 3.2 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and verify that the complete package test suite passes.
- [x] 3.3 Run `openspec validate --all --json --no-interactive` and verify that the change artifacts and repository specifications validate without errors.
- [x] 3.4 Run the documented installer dry run and verify that the plan contains the updated `custom-openspec-grill/SKILL.md` without modifying user-level files.

HUMAN UAT - NOT APPLICABLE: Contract tests, adapter tests, package validation,
OpenSpec validation, and the installer dry run cover the acceptance behavior.
No manual user action adds coverage for this change.
