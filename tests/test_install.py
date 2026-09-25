from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from custom_openspec_workflow.install import install_user


PROJECT_ROOT = Path(__file__).parents[1]
SOURCE_PACKAGE = PROJECT_ROOT / "src" / "custom_openspec_workflow"


class InstallTests(unittest.TestCase):
    def test_environment_configured_host_locations_are_used(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            skills_dir = root / "configured-skills"
            bin_dir = root / "configured-bin"
            skills_dir.mkdir()
            bin_dir.mkdir()

            with patch.dict(
                os.environ,
                {
                    "HOME": str(home),
                    "CUSTOM_OPENSPEC_WORKFLOW_HOST": "codex",
                    "CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR": str(skills_dir),
                    "CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR": str(bin_dir),
                },
            ):
                payload = install_user(source_root=SOURCE_PACKAGE)

            self.assertEqual(payload["skillsDir"], str(skills_dir))
            self.assertEqual(payload["binDir"], str(bin_dir))
            self.assertTrue((bin_dir / "custom-openspec-init").is_file())

    def test_default_install_copies_renamed_package_and_generates_working_wrappers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            skills_dir = root / "skills"
            bin_dir = root / "bin"

            with patch.dict(os.environ, {"HOME": str(home)}):
                payload = install_user(
                    skills_dir=skills_dir,
                    bin_dir=bin_dir,
                    source_root=SOURCE_PACKAGE,
                )

            destination = home / ".local" / "share" / "custom-openspec-workflow"
            copied_package = destination / "custom_openspec_workflow"
            self.assertEqual(payload["installDir"], str(destination))
            self.assertTrue((copied_package / "__init__.py").is_file())
            self.assertTrue((skills_dir / "custom-openspec-grill" / "SKILL.md").is_file())

            init_wrapper = bin_dir / "custom-openspec-init"
            grill_wrapper = bin_dir / "custom-openspec-grill"
            init_text = init_wrapper.read_text(encoding="utf-8")
            grill_text = grill_wrapper.read_text(encoding="utf-8")
            self.assertIn("from custom_openspec_workflow.bootstrap import main", init_text)
            self.assertIn("from custom_openspec_workflow.grill_cli import main", grill_text)

            for wrapper in (init_wrapper, grill_wrapper):
                result = subprocess.run(
                    [str(wrapper), "--help"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_explicit_install_directory_overrides_default_data_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            explicit = root / "explicit-install"
            environment_skills = root / "environment-skills"
            environment_bin = root / "environment-bin"
            explicit_skills = root / "skills"
            explicit_bin = root / "bin"

            with patch.dict(
                os.environ,
                {
                    "HOME": str(home),
                    "CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR": str(environment_skills),
                    "CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR": str(environment_bin),
                },
            ):
                payload = install_user(
                    skills_dir=explicit_skills,
                    bin_dir=explicit_bin,
                    install_dir=explicit,
                    source_root=SOURCE_PACKAGE,
                )

            self.assertEqual(payload["installDir"], str(explicit))
            self.assertTrue((explicit / "custom_openspec_workflow" / "install.py").is_file())
            self.assertFalse((home / ".local" / "share" / "custom-openspec-workflow").exists())
