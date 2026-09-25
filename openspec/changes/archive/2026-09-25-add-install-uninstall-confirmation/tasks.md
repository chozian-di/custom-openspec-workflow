# Tasks

## 1. Add planning and ownership primitives

- [x] 1.1 Add the install and uninstall plan model, path enumeration, operation labels, and JSON fields in `src/custom_openspec_workflow/install.py`; verify that disposable plan tests list every package, skill, wrapper, manifest, conflict, and cleanup path without writing files.
- [x] 1.2 Add manifest serialization, content hashing, file mode recording, and ownership preflight checks; verify fresh install, repeated install, unmanaged conflict, modified managed file, and missing manifest tests.
- [x] 1.3 Add persistent tests for plan enumeration, manifest hashes and modes, fresh installs, repeated installs, unmanaged conflicts, modified managed files, and missing manifests; verify blocked operations write no target files.

## 2. Add guarded install and confirmation behavior

- [x] 2.1 Refactor installation to stage package and wrapper content, apply atomic file replacements, preserve the prior managed state on failure, and publish the manifest only after a complete install; verify existing installed-wrapper smoke tests and rollback tests pass.
- [x] 2.2 Add `--uninstall`, `-y`, and `--yes` parser options and interactive confirmation handling; verify decline leaves all paths unchanged, both yes options skip the prompt, non-interactive use fails without an explicit yes option, and JSON output remains machine-readable.
- [x] 2.3 Add persistent CLI tests for plan display, cancellation, both confirmation aliases, JSON plan ordering, dry-run, and non-interactive refusal; verify the plan appears before confirmation or writes and final JSON output remains parseable.

## 3. Add safe user-level uninstall

- [x] 3.1 Implement `custom-openspec-install --uninstall` from the ownership manifest; verify that unchanged package files, the custom skill, wrappers, and the manifest are removed while the data root, Grill staging sessions, and unrelated files remain.
- [x] 3.2 Preserve and report modified managed files during uninstall and refuse untrusted manifest-free removal; verify that user edits survive while safe unchanged files can still be removed.
- [x] 3.3 Verify that uninstall does not inspect or modify a disposable repository's `openspec`, `.agents`, source files, or OpenSpec global configuration fixture.
- [x] 3.4 Add persistent uninstall tests for unchanged removal, modified-file preservation, manifest-free refusal, repository boundaries, unrelated data, and upgrade cleanup; verify user and repository sentinel files remain unchanged.

## 4. Document the user-facing workflow

- [x] 4.1 Update `README.md` with the install plan, confirmation prompt, `-y` and `--yes`, dry-run, JSON, and non-interactive examples; verify every documented command matches the CLI help and behavior.
- [x] 4.2 Document `--uninstall`, manifest ownership, conflict handling, modified-file preservation, upgrade behavior, and the boundary between user-level uninstall and repository bootstrap; verify the README does not claim that uninstall rolls back `custom-openspec-init`.

## 5. Run integration validation

- [x] 5.1 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and verify the complete test suite passes.
- [x] 5.2 Run the disposable validation matrix and `openspec validate --all --json --no-interactive`; verify the new installer scenarios and all existing OpenSpec artifacts pass validation.

## 6. Address verification follow-ups

- [x] 6.1 Clarify JSON stream behavior in `README.md`. State that a write-mode JSON command writes the complete plan to standard error and the final result object to standard output. Verify that the documented text matches the command behavior.
- [x] 6.2 Make extra-path scan order deterministic in `src/custom_openspec_workflow/install.py`. Add a test that creates conflicts in both scan roots and verifies stable JSON plan ordering. Run the full test suite and OpenSpec validation.
- [x] 6.3 Remove manifest-free install adoption from `src/custom_openspec_workflow/install.py`; verify that fresh empty installs still create a manifest, while existing package, skill, wrapper, or extra managed-root files without a trustworthy manifest cause a conflict and write no target files.
- [x] 6.4 Add persistent tests for strict manifest ownership; verify that a complete pre-populated target without a manifest is refused and that a fresh empty target installs successfully.
