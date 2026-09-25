from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from custom_openspec_workflow.host import discover_host


class HostDiscoveryTests(unittest.TestCase):
    def test_discovery_reads_project_namespace_environment_variables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_dir = root / "skills"
            bin_dir = root / "bin"
            skills_dir.mkdir()
            bin_dir.mkdir()

            with patch.dict(
                os.environ,
                {
                    "CUSTOM_OPENSPEC_WORKFLOW_HOST": "codex",
                    "CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR": str(skills_dir),
                    "CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR": str(bin_dir),
                    "PATH": "",
                },
            ):
                layout = discover_host()

            self.assertEqual(layout.name, "codex")
            self.assertEqual(layout.skills_dir, skills_dir)
            self.assertEqual(layout.bin_dir, bin_dir)

    def test_missing_configured_locations_report_new_variable_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            missing_skills = Path(directory) / "missing-skills"
            missing_bin = Path(directory) / "missing-bin"
            with patch.dict(
                os.environ,
                {
                    "CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR": str(missing_skills),
                    "CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR": str(missing_bin),
                    "HOME": str(Path(directory) / "home"),
                    "PATH": "",
                },
            ):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR",
                ):
                    discover_host()
