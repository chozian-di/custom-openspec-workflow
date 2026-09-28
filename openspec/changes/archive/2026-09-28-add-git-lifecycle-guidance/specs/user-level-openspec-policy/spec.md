# Spec Delta

## ADDED Requirements

### Requirement: Recommend separable outcome commits after Archive

The package policy SHALL recommend separate, advisory commits for the archived `openspec/` content and the non-OpenSpec outcome after successful Archive. The OpenSpec commit SHALL use an explicit file list that contains only the archived change's intended OpenSpec paths. The outcome commit SHALL use an explicit file list that contains only the intended non-OpenSpec paths for that change. The guidance MUST NOT include unrelated worktree changes or require a second commit when no non-OpenSpec outcome exists.

#### Scenario: Archive and implementation changes are both uncommitted

- **WHEN** successful Archive leaves the archived change and its implementation changes uncommitted
- **THEN** the guidance recommends one OpenSpec Archive commit and one non-OpenSpec outcome commit with separate explicit file lists

#### Scenario: Multiple OpenSpec changes are active

- **WHEN** successful Archive moves one change while other OpenSpec changes remain active
- **THEN** the OpenSpec commit includes only the archived change's intended paths

#### Scenario: Unrelated worktree changes exist

- **WHEN** unrelated changes exist outside the completed change
- **THEN** the guidance leaves those paths out of the recommended commit file lists

#### Scenario: No non-OpenSpec outcome exists

- **WHEN** successful Archive produces no intended non-OpenSpec changes for the completed change
- **THEN** the guidance recommends only the OpenSpec Archive commit

### Requirement: Document outcome-focused Git practices

The package policy and README SHALL recommend `type(scope): subject` commit messages, commits that describe outcomes rather than process, normal execution of repository hooks, warnings before commits on `main`, `master`, `trunk`, `staging`, `develop`, `development`, or `dev`, `git revert --no-commit` for agent-initiated rollback, and squash merges without requiring them. The guidance SHALL state that the package does not install project `pre-commit` or `commit-msg` hooks and SHALL not use `--no-verify` by default. All of these recommendations SHALL remain advisory.

#### Scenario: User reviews the commit policy

- **WHEN** the user reads the package Git guidance
- **THEN** the guidance includes the selected message style, explicit file lists, outcome-focused commits, protected-branch warnings, rollback preference, and squash-merge recommendation

#### Scenario: A repository has commit hooks

- **WHEN** a project has `pre-commit` or `commit-msg` hooks
- **THEN** the guidance leaves those hooks enabled and does not recommend `--no-verify` by default

#### Scenario: A commit targets a common protected branch

- **WHEN** a recommended commit targets one of the listed common protected branch names
- **THEN** the guidance warns the user without claiming that the branch is actually protected or blocking the commit

#### Scenario: Agent-initiated rollback is needed

- **WHEN** the agent recommends reversing an earlier commit
- **THEN** the guidance prefers `git revert --no-commit` so the user can review the rollback before committing it

#### Scenario: User chooses a merge strategy

- **WHEN** the user or repository chooses how to merge the completed work
- **THEN** the guidance recommends squash merging but does not require it

### Requirement: Suggest Git initialization without automatic mutation

When a post-Archive commit recommendation becomes relevant and the project root has no Git repository, the guidance SHALL suggest `git init`. The package MUST NOT run `git init` automatically and MUST NOT create or modify `.git` as part of the suggestion.

#### Scenario: Project has no Git repository after Archive

- **WHEN** successful Archive completes and the project root has no Git repository
- **THEN** the guidance suggests `git init` and waits for the user's action

#### Scenario: Project already has a Git repository

- **WHEN** successful Archive completes and the project root is already in a Git repository
- **THEN** the guidance does not suggest initializing another repository
