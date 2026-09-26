# Tasks

## 1. Collect prerequisite results

- [x] 1.1 Add structured prerequisite result data to the install plan and collect the `grill-me` and default `openspec` results from the selected installation context. Make sure that missing feature prerequisites do not create file conflicts or block an otherwise safe install plan.
- [x] 1.2 Add unit coverage for available and missing `grill-me`, missing `openspec`, explicit skills directories, and fresh target paths. Run the focused install tests and make sure that the checks do not write files or claim upstream ownership.

## 2. Report results through installer output

- [x] 2.1 Add prerequisite results to human plan output and keep missing warnings before the confirmation prompt. Run the focused CLI tests and make sure that cancellation and `--yes` behavior remain unchanged.
- [x] 2.2 Add prerequisite results to JSON plans, final JSON results, and dry-run results. Run the JSON installer tests and make sure that standard output contains one parseable final result and standard error contains the pre-apply plan.
- [x] 2.3 Keep prerequisite checks out of uninstall planning and add regression coverage for uninstall with missing upstream skills and commands. Run the focused uninstall tests and make sure that upstream and user-owned files remain unchanged.

## 3. Provide consistent setup guidance

- [x] 3.1 Update the custom Grill skill and compatibility failure guidance with the checked location, `satya-janghu/agent-skills`, the `skills/grill-me` path, and the README reference. Run the Grill and skill contract tests and make sure that missing dependency handling remains non-destructive.
- [x] 3.2 Add a README prerequisite section that explains the advisory warning, the upstream Grill Me installation path, the default `openspec` command requirement, and the explicit executable override. Read each documented command and make sure that it matches the implemented output and flags.

## 4. Run integration checks

- [x] 4.1 Run the full Python test suite and make sure that all tests pass.
- [x] 4.2 Run OpenSpec validation for the repository and make sure that the change artifacts and the existing specifications remain valid.
