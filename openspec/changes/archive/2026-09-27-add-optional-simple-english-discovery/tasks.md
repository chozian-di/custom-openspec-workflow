# Tasks

## 1. Add Simple English discovery

- [x] 1.1 Add shared skill-name discovery and preserve the existing `grill-me` discovery behavior. Add `simple-english` source constants, remediation text, and discovery. Add direct, nested, missing, and mismatched-name tests. Verify the focused skill discovery tests pass.
- [x] 1.2 Add the available or missing `simple-english` result to the install plan. Add the brief value statements for both optional skills to the structured prerequisite results. Keep the results non-blocking and outside `expected_files` and the ownership manifest. Add install-plan tests for selected skills directories, missing prerequisites, and value statements. Verify the focused install-plan tests pass.

## 2. Preserve installer behavior

- [x] 2.1 Include the new result and its value statement in human-readable plans, JSON plans, final JSON results, and dry runs. Show the `grill-me` and `simple-english` value statements whether each skill is available or missing. Update tests for warning order, parseable output, value fields, and the complete prerequisite name set. Verify the focused CLI and JSON tests pass.
- [x] 2.2 Keep prerequisite discovery out of uninstall planning and preserve upstream and unrelated files. Update the uninstall regression tests for missing Simple English. Verify the focused uninstall tests pass.
- [x] 2.3 Add the Simple English fixture and extend the disposable validation matrix to cover available discovery without copying or modifying the upstream skill. Verify the matrix test passes.

## 3. Document the optional dependency

- [x] 3.1 Update `README.md` with the optional Simple English prerequisite, the `AminBlg/SimpleEnglish` source, the `skills/simple-english` path, the skill-only install guidance, and the non-owning behavior. Add detailed descriptions of the value that Grill Me and Simple English provide, and keep those descriptions aligned with the brief statements shown during installation. Update README contract assertions. Verify the documentation tests pass and every documented command uses the implemented flags.
- [x] 3.2 Update `docs/compatibility-baseline.md` with the observed Simple English version, upstream commit, skill path, and name-discovery contract. Verify the compatibility record matches the upstream `SKILL.md` metadata read during implementation.

## 4. Run integration checks

- [x] 4.1 Run the full Python test suite with the repository `src` path available and verify all tests pass from the active OpenSpec change state.
- [x] 4.2 Run `openspec validate --all --json --no-interactive` and verify the change delta and existing specifications remain valid.
