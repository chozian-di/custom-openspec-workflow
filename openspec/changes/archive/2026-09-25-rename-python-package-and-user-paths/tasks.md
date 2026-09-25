# Tasks

## 1. Rename the Python package namespace

- [x] 1.1 Rename `src/custom_openspec` to `src/custom_openspec_workflow` and update project and test imports. Verify that active source, test, and script files contain no old Python import or source path.
- [x] 1.2 Update `pyproject.toml`, package resource lookups, and console entry point targets for `custom_openspec_workflow`. Verify that the package imports from the source tree and that its policy and Grill skill resources load.
- [x] 1.3 Update package namespace tests and add coverage for the renamed package resource lookup. Verify the focused package and resource tests pass.

## 2. Update user-level paths and configuration variables

- [x] 2.1 Add shared path helpers for the default data root and use `~/.local/share/custom-openspec-workflow` for installation and Grill staging. Verify that home-directory calculation occurs at call time and that explicit path arguments still take precedence.
- [x] 2.2 Update the installer to copy `custom_openspec_workflow` and generate wrappers that import the renamed modules. Add installer tests for the default destination, copied package directory, wrapper target, and explicit `--install-dir`. Verify the tests use disposable directories.
- [x] 2.3 Rename host and Grill environment variables to the `CUSTOM_OPENSPEC_WORKFLOW_*` namespace. Update error messages and test both new variables and explicit command-line overrides.
- [x] 2.4 Update the README installation, staging, and configuration examples with the new package path, data root, staging root, and environment variables. Verify that active documentation contains no old path or variable names.

## 3. Run integration checks

- [x] 3.1 Run the full Python test suite and verify that all tests pass with the renamed package and paths.
- [x] 3.2 Build a wheel and inspect its contents. Verify that the wheel contains the `custom_openspec_workflow` package and both declared data resources.
- [x] 3.3 Run the installer and Grill staging smoke checks in disposable directories. Verify that the generated helpers run, the default paths match the specifications, and the old names are not used at runtime.
- [x] 3.4 Run `openspec validate --all --json --no-interactive` and verify that the repository remains valid with unchanged capability IDs.

HUMAN UAT - NOT APPLICABLE: Automated unit, integration, packaging, and OpenSpec validation checks cover the changed behavior.
