# Tasks

## 1. Add the license and package metadata

- [x] 1.1 Add the standard MIT License text to the root `LICENSE` file with `Copyright (c) 2026 Chris Hozian`, and verify that the file contains the permission and warranty sections from the standard text.
- [x] 1.2 Add `license = { file = "LICENSE" }` to `[project]` and `license-files = ["LICENSE"]` to `[tool.setuptools]` in `pyproject.toml`, and verify that the TOML parses and the configured license file exists.

## 2. Document the license

- [x] 2.1 Add a `License` section to `README.md` with a link to `LICENSE`, and verify that the link resolves to the root license file and names the MIT License.

## 3. Verify the packaged result

- [x] 3.1 Build a source distribution and wheel in a temporary output directory, and verify that each archive contains `LICENSE` and that the wheel metadata identifies the MIT License.
- [x] 3.2 Run `PYTHONPATH=src python3 -m unittest discover -s tests -v` and `openspec validate --all --json --no-interactive`, and verify that both commands pass with the new license files present.
