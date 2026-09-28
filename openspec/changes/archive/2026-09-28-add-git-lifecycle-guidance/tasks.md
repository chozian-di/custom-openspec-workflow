# Tasks

## 1. Add canonical Git lifecycle policy

- [x] 1.1 Update `src/custom_openspec_workflow/data/openspec-policy.yaml` so normal Apply work does not recommend commits, an explicit user pause recommends `docs(openspec): checkpoint <change-name>`, and the policy remains advisory. Verify the YAML parses and the existing policy merge tests pass.
- [x] 1.2 Update the Archive guidance in `src/custom_openspec_workflow/data/openspec-policy.yaml` with the successful-Archive commit boundary, separate OpenSpec and non-OpenSpec commits, explicit file lists, GSD-style messages, hook handling, protected-branch warnings, rollback preference, squash recommendation, and non-automatic `git init`. Verify the policy contains every selected branch name and no automatic Git action.
- [x] 1.3 Extend the policy contract tests to cover the normal lifecycle boundary, explicit pause exception, two-commit structure, `--no-verify` guidance, protected-branch candidates, `git revert --no-commit`, squash recommendation, and `git init` suggestion. Verify the focused policy tests pass without modifying a real `.git` directory.

## 2. Document the user-facing workflow

- [x] 2.1 Add a README Git lifecycle section that explains when commit guidance appears, when it does not, and how explicit pause checkpoints differ from post-Archive commits. Verify the README examples match the canonical policy wording.
- [x] 2.2 Document the two-commit default with explicit path examples, the `type(scope): subject` message form, outcome-focused history, normal hook execution, protected-branch warnings for `main`, `master`, `trunk`, `staging`, `develop`, `development`, and `dev`, `git revert --no-commit`, squash-merge recommendation, and non-automatic `git init`. Verify the README contains the selected guidance and excludes routine pre-Archive safety commits and automatic Git mutation.
- [x] 2.3 Extend README and lifecycle contract tests for commit timing, path separation, protected-branch names, hook behavior, and repository initialization. Verify the focused documentation tests pass.

## 3. Validate the integrated package behavior

- [x] 3.1 Run the full Python unit test suite and verify policy merge, bootstrap idempotence, rollback, and existing lifecycle evidence remain passing.
- [x] 3.2 Run `openspec validate --all --json --no-interactive` and verify the repository and the new change artifacts validate without changing native OpenSpec behavior.
- [x] 3.3 Run the validation matrix and verify the post-Archive guidance remains advisory, uses the stock schema, and does not create commits, hooks, branches, worktrees, or `.git` state.
