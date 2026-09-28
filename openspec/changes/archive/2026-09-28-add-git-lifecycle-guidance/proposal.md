# Proposal

## Why

The workflow currently explains that Git owns commits and source isolation, but it does not give a consistent commit policy for completed OpenSpec changes. Agents can also suggest commits at times that interrupt normal OpenSpec planning and implementation. The package needs one advisory policy that preserves the OpenSpec lifecycle and produces separable, reviewable Git history after Archive.

## What Changes

- Add advisory Git guidance that does not replace native OpenSpec commands or user decisions.
- Recommend Git commits only after successful Archive during normal work.
- Allow an earlier OpenSpec checkpoint only when the user explicitly requests a pause.
- Recommend separate commits for the archived `openspec/` content and the non-OpenSpec implementation outcome.
- Require explicit file lists in recommended commit commands.
- Use the GSD-compatible `type(scope): subject` commit message form.
- Recommend outcome-focused commits, normal hook execution, protected-branch warnings, reviewable `git revert --no-commit` rollback, and squash merges.
- Suggest `git init` when no repository exists, without running it automatically.
- Treat `main`, `master`, `trunk`, `staging`, `develop`, `development`, and `dev` as common protected-branch warning candidates.
- Do not add hook installation, hard Git enforcement, automatic commits, automatic staging, automatic Git initialization, routine pre-Archive safety commits, or a separate `wip` commit type.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `openspec-lifecycle-guardrails`: define the timing and advisory limits for post-Archive commits and explicit pause checkpoints.
- `user-level-openspec-policy`: document the separable commit structure, message style, file-list, hook, branch, rollback, merge, and repository initialization guidance.

## Impact

- Update `src/custom_openspec_workflow/data/openspec-policy.yaml` so bootstrap carries the new Apply and Archive guidance.
- Update `README.md` with the Git lifecycle policy and examples.
- Update the two affected OpenSpec capability specifications.
- Extend policy and documentation contract tests.
- No OpenSpec executable, generated OpenSpec skill, custom Git command, hook, or automatic repository mutation will be added.
