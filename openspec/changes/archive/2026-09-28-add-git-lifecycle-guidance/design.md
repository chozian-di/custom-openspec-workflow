# Design

## Context

See `proposal.md` for the motivation and scope. The package already uses the
supported OpenSpec policy file, `operations.apply.guidance`,
`operations.archive.guidance`, README guidance, and contract tests. OpenSpec
owns the commands, schema, task state, and Archive behavior. Git owns commits,
branches, worktrees, merges, rebases, and source isolation.

The policy file is merged into target repositories by `custom-openspec-init`.
The package has no Git command runner and does not install project hooks.

## Goals / Non-Goals

Goals:

- Keep commit recommendations at the selected lifecycle boundaries.
- Preserve a separate OpenSpec Archive commit and implementation outcome commit.
- Keep all Git recommendations advisory and user-controlled.
- Make the guidance work with project-owned hooks and repository policies.
- Keep the package compatible with stock OpenSpec behavior and the existing
  bootstrap and upgrade path.

Non-goals:

- Do not implement Git command execution, staging, or commit automation.
- Do not install, configure, or bypass project hooks.
- Do not create a custom OpenSpec command or generated skill.
- Do not manage branches or worktrees.
- Do not add routine pre-Archive safety commits or a separate `wip` type.
- Do not require squash merges or claim that branch names prove protection.

## Decisions

### Use supported policy and documentation surfaces

Add the operational guidance to
`src/custom_openspec_workflow/data/openspec-policy.yaml`. Add the user-facing
explanation and examples to `README.md`. Keep the implementation limited to
the supported policy merge. This keeps the package independent of OpenSpec
internals and preserves native command behavior.

### Keep the normal commit boundary after successful Archive

Add the no-commit recommendation to Apply guidance for normal work. Add the
explicit pause checkpoint exception to the same guidance. Add the successful
Archive commit recommendation to Archive guidance after the native Archive
result is known. The guidance will not recommend a commit while Archive is
running or after a failed Archive.

The Archive recommendation will describe one OpenSpec commit followed by one
non-OpenSpec outcome commit when both categories contain intended changes. It
will use explicit file lists and exclude unrelated worktree paths. It will not
force a second commit when no non-OpenSpec outcome exists.

### Use advisory heuristics for Git safety

Document the GSD-compatible `type(scope): subject` form, outcome-focused
commits, normal hook execution, `git revert --no-commit`, and squash-merge
recommendations. Warn on the selected common branch names without querying or
claiming server-side branch protection. Keep `--no-verify` out of normal
recommendations. A user-directed exception remains possible.

### Suggest Git initialization only at the commit boundary

When the post-Archive commit recommendation becomes relevant and no Git root
exists, the guidance will suggest `git init`. It will not run the command or
modify `.git`. The guidance will not suggest initialization during earlier
OpenSpec stages.

### Test the policy contract without testing Git side effects

Extend the existing policy and README contract tests. Check the lifecycle
timing, commit separation, file-list language, message format, hook behavior,
branch warning names, rollback preference, squash recommendation, and
non-automatic Git initialization. Run native OpenSpec validation and the
existing unit and validation matrix tests. No test will create commits or
modify a real repository's `.git` directory.

## Risks / Trade-offs

- [Risk] A commit recommendation can still interrupt a user who does not want
  Git guidance. -> Mitigation: limit normal recommendations to successful
  Archive and make the earlier checkpoint depend on an explicit pause request.

- [Risk] A branch name can look protected without server-side protection. ->
  Mitigation: call these names warning candidates and do not claim protection
  or block the user.

- [Risk] A project hook can reject a recommended commit. -> Mitigation: leave
  hooks enabled, report the hook result, and do not add `--no-verify` unless the
  user explicitly directs it.

- [Risk] A broad file list can include unrelated work. -> Mitigation: require
  explicit paths for each commit and stage the archived change separately from
  the non-OpenSpec outcome.

- [Risk] Existing target repositories already contain older policy guidance. ->
  Mitigation: use the existing canonical policy merge and document the normal
  package update and bootstrap path.

## Migration Plan

1. Update the canonical policy and README.
2. Update the affected capability specifications and contract tests.
3. Run the package tests, validation matrix, and native OpenSpec validation.
4. Install the updated package through the normal installer.
5. Run `custom-openspec-init` in target repositories to merge the updated
   supported policy entries.

To roll back, revert the package change, reinstall the previous package, and
run the normal bootstrap update. The change does not alter repository source
files or `.git` state automatically.

## Open Questions

None. The user selected the lifecycle boundary, commit structure, branch
warning names, and non-automatic behavior before this design was written.
