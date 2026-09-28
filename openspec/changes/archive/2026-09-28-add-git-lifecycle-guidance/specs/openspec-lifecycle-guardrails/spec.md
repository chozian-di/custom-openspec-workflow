# Spec Delta

## ADDED Requirements

### Requirement: Limit Git commit recommendations to explicit lifecycle boundaries

The workflow guidance SHALL present Git commit recommendations as advisory. During normal Explore, Propose, Apply, Update, Verify, UAT, and pre-Archive work, the guidance MUST NOT recommend a Git commit. After native Archive completes successfully, the guidance SHALL strongly recommend the relevant Git commits before the session ends. If the user explicitly requests a pause before Archive, the guidance SHALL recommend an interrupted-handoff checkpoint. The guidance MUST NOT recommend a commit while Archive is running or after Archive reports failure.

#### Scenario: Normal work remains before Archive

- **WHEN** the user works through normal OpenSpec planning, implementation, acceptance, or verification without requesting a pause
- **THEN** the guidance does not recommend a Git commit

#### Scenario: User requests a pause before Archive

- **WHEN** the active change is incomplete and the user explicitly requests a pause
- **THEN** the guidance recommends an advisory checkpoint such as `docs(openspec): checkpoint <change-name>` without marking unfinished tasks complete

#### Scenario: Archive completes successfully

- **WHEN** native Archive completes successfully for the active change
- **THEN** the guidance strongly recommends the relevant Git commits before the session ends

#### Scenario: Archive is running or fails

- **WHEN** native Archive is still running or reports failure
- **THEN** the guidance does not recommend an Archive commit until the Archive result is understood and successful

#### Scenario: Session ends without Archive or an explicit pause

- **WHEN** the session ends while an active change remains incomplete and the user did not explicitly request a pause
- **THEN** the guidance does not create or recommend an interrupted-handoff commit
