# Tasks

## 1. Add the cache path and launcher behavior

- [x] 1.1 Add `default_cache_root()` with the `~/.cache/custom-openspec-workflow` default and update `tests/test_paths.py` to verify call-time home selection.
- [x] 1.2 Update generated helper wrappers to set `PYTHONPYCACHEPREFIX` before Python starts, preserve a user-provided value, and keep the installed package first on `sys.path`; update `tests/test_install.py` to verify wrapper content and execution.
- [x] 1.3 Update `scripts/custom-openspec-install`, `scripts/custom-openspec-init`, and `scripts/custom-openspec-grill` to set the same default before Python starts, and verify the launchers with disposable cache paths.
- [x] 1.4 Update `README.md` to document the persistent package path, the default bytecode cache path, the standard override, and the cache behavior during uninstall; verify the examples match the implemented launchers.

## 2. Verify cache isolation and installer ownership

- [x] 2.1 Add a disposable installed-helper test that runs without a cache override, confirms that package-local `__pycache__` files are absent, and confirms that generated `.pyc` files exist under the cache root.
- [x] 2.2 Add coverage for an explicit `PYTHONPYCACHEPREFIX` value, manifest exclusion, and uninstall preservation of generated cache data; verify that no cache path is treated as an installer conflict or owned file.

## 3. Run integration checks

- [x] 3.1 Run the full Python test suite with the project test command and verify that all tests pass.
- [x] 3.2 Build a wheel and inspect its contents to verify that the package resources remain in the persistent package and no cache files enter the wheel.
- [x] 3.3 Run the installer and generated helpers in disposable directories, then run `openspec validate --all --json --no-interactive` and verify the cache, packaging, and OpenSpec checks pass.

HUMAN UAT - NOT APPLICABLE: Automated path, launcher, runtime, ownership, packaging, and OpenSpec checks cover the acceptance criteria.
