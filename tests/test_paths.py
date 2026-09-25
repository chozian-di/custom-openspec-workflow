from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from custom_openspec_workflow import PACKAGE_NAME
from custom_openspec_workflow.paths import (
    default_cache_root,
    default_data_root,
    default_grill_staging_dir,
    grill_skill_path,
    package_data_path,
    policy_path,
)


class PackagePathTests(unittest.TestCase):
    def test_package_namespace_and_resources_use_renamed_package(self) -> None:
        self.assertEqual(PACKAGE_NAME, "custom-openspec-workflow")

        policy = package_data_path("openspec-policy.yaml")
        skill = package_data_path("custom-openspec-grill/SKILL.md")

        self.assertEqual(policy, policy_path())
        self.assertEqual(skill, grill_skill_path())
        self.assertTrue(policy.is_file())
        self.assertTrue(skill.is_file())
        self.assertIn("rules:", policy.read_text(encoding="utf-8"))
        self.assertIn("name: custom-openspec-grill", skill.read_text(encoding="utf-8"))

    def test_default_data_root_is_calculated_for_the_current_home(self) -> None:
        with tempfile.TemporaryDirectory() as first_directory:
            with tempfile.TemporaryDirectory() as second_directory:
                with patch.dict(os.environ, {"HOME": first_directory}):
                    first = default_data_root()
                with patch.dict(os.environ, {"HOME": second_directory}):
                    second = default_data_root()

        self.assertEqual(first, Path(first_directory) / ".local" / "share" / "custom-openspec-workflow")
        self.assertEqual(second, Path(second_directory) / ".local" / "share" / "custom-openspec-workflow")
        self.assertNotEqual(first, second)

    def test_default_cache_root_is_calculated_for_the_current_home(self) -> None:
        with tempfile.TemporaryDirectory() as first_directory:
            with tempfile.TemporaryDirectory() as second_directory:
                with patch.dict(os.environ, {"HOME": first_directory}):
                    first = default_cache_root()
                with patch.dict(os.environ, {"HOME": second_directory}):
                    second = default_cache_root()

        self.assertEqual(first, Path(first_directory) / ".cache" / "custom-openspec-workflow")
        self.assertEqual(second, Path(second_directory) / ".cache" / "custom-openspec-workflow")
        self.assertNotEqual(first, second)

    def test_grill_default_uses_project_root_or_explicit_environment_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "home"
            override = Path(directory) / "staging"
            with patch.dict(os.environ, {"HOME": str(home)}, clear=False):
                os.environ.pop("CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME", None)
                self.assertEqual(
                    default_grill_staging_dir(),
                    home / ".local" / "share" / "custom-openspec-workflow" / "grill",
                )
                with patch.dict(
                    os.environ,
                    {"CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME": str(override)},
                ):
                    self.assertEqual(default_grill_staging_dir(), override)
