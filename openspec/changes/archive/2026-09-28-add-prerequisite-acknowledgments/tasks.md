# Tasks

## 1. Add installer acknowledgment and OpenSpec guidance

- [x] 1.1 Add shared OpenSpec installation guidance with the npm install
  command, the `openspec --version` check, and the
  `--openspec-executable /path/to/openspec` override. Make sure that the
  installer never invokes a package manager, and verify the guidance tests
  contain all three facts.
- [x] 1.2 Update the install plan and confirmation path so a missing OpenSpec
  warning states that the workflow cannot function until OpenSpec is installed.
  Make sure that `-y` and `--yes` count as acknowledgment, that a declined
  prompt writes nothing, and that dry-run and JSON behavior remain correct.
  Run the focused installer tests for cancellation, `--yes`, dry-run, JSON,
  and conflict handling.
- [x] 1.3 Update the README prerequisite and install sections with the external
  OpenSpec installation commands, version check, explicit executable override,
  acknowledgment behavior, and the fact that this installer does not install
  OpenSpec. Verify the documented commands and warning text with the README
  contract tests.

## 2. Add bootstrap preflight reporting

- [x] 2.1 Add an early executable check to `custom-openspec-init` for the
  default `openspec` command and explicit executable values. Make sure that a
  missing executable stops before global or repository changes and reports the
  installation guidance. Verify the existing bootstrap tests still pass.
- [x] 2.2 Add bootstrap tests for a missing default command, a runnable
  explicit executable, and an unavailable explicit path. Verify that each
  failure reports the selected command and leaves target and global files
  unchanged.

## 3. Align Grill Me missing-dependency output

- [x] 3.1 Update the Grill adapter, compatibility output, and installed
  `custom-openspec-grill` skill with one clear missing-dependency message. Make
  sure that the message names the checked directory, `satya-janghu/agent-skills`,
  `skills/grill-me`, and the README, and states that normal OpenSpec work stays
  available. Verify the existing skill contract remains free of copied Grill
  Me question logic.
- [x] 3.2 Add or update Grill tests for missing dependency output, available
  dependency behavior, unchanged source material, and compatibility JSON.
  Run the focused Grill and skill contract tests.

## 4. Run integration checks

- [x] 4.1 Run the full Python test suite with
  `PYTHONPATH=src python3 -m unittest discover -s tests -v` and resolve any
  failures.
- [x] 4.2 Run `openspec validate --all --json --no-interactive` and verify that
  the change artifacts and the existing specifications pass validation.
