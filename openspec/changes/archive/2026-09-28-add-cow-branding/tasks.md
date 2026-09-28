# Tasks

## 1. Add the runtime identity to public command surfaces

- [x] 1.1 Add display-only constants for `COW` and "chozian's OpenSpec Workflow" beside the existing package constants, preserve `PACKAGE_NAME`, and verify the package path tests still expect `custom-openspec-workflow`.
- [x] 1.2 Update top-level help for `custom-openspec-install`, `custom-openspec-init`, and `custom-openspec-grill`, and update human-readable installer plan, result, and refusal text with the brief identity statement. Verify each command's `--help` output and the installer's non-JSON output contain the official name, `COW`, and the alternate name.
- [x] 1.3 Extend installer and validation-matrix tests to cover the new help and human-readable identity text, and verify installer `--json` output remains valid with the existing fields and without human-only branding text.

## 2. Add the identity to static project surfaces

- [x] 2.1 Add the official-name, short-name, and alternate-name explanation near the start of `README.md`, update the package description in `pyproject.toml`, and verify the README keeps the existing workflow and Git-lifecycle content.
- [x] 2.2 Add one brief identity statement to the installed `custom-openspec-grill` skill and extend the skill and documentation contract tests. Verify the required identity phrases appear in the skill, README, and package metadata without changing the skill front matter name.

## 3. Validate the complete branding change

- [x] 3.1 Run the focused package, installer, skill, and validation-matrix tests and verify command names, imports, paths, environment-variable names, manifest format, and JSON output remain unchanged.
- [x] 3.2 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v`, `openspec validate --all --json --no-interactive`, and `git diff --check`. Record `HUMAN UAT - NOT APPLICABLE: Automated tests cover the identity text and preservation of machine-facing contracts.`

HUMAN UAT - NOT APPLICABLE: Automated tests cover the identity text and preservation of machine-facing contracts.
