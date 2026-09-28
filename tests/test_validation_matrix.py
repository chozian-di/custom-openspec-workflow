from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from custom_openspec_workflow.grill import REQUIRED_SECTIONS
from custom_openspec_workflow import (
    PACKAGE_NAME,
    PROJECT_ALTERNATE_NAME,
    PROJECT_SHORT_NAME,
)


PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES = PROJECT_ROOT / "tests" / "fixtures"


def run_script(
    script: str,
    *arguments: str,
    environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(PROJECT_ROOT / "scripts" / script), *arguments],
        cwd=PROJECT_ROOT,
        env=environment,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class ValidationMatrixTests(unittest.TestCase):
    def test_disposable_install_matrix_discovers_simple_english_without_modifying_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_dir = FIXTURES / "upstream-skills"
            upstream_files = {
                path: path.read_bytes()
                for path in skills_dir.rglob("*")
                if path.is_file()
            }
            environment = os.environ.copy()
            environment["HOME"] = str(root / "home")
            environment["PYTHONPYCACHEPREFIX"] = str(root / "cache")

            result = run_script(
                "custom-openspec-install",
                "--source-root",
                str(PROJECT_ROOT / "src" / "custom_openspec_workflow"),
                "--skills-dir",
                str(skills_dir),
                "--bin-dir",
                str(root / "bin"),
                "--install-dir",
                str(root / "install"),
                "--json",
                "--dry-run",
                environment=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            prerequisites = {item["name"]: item for item in payload["prerequisites"]}
            self.assertEqual(prerequisites["grill-me"]["status"], "available")
            self.assertEqual(prerequisites["simple-english"]["status"], "available")
            self.assertEqual(
                prerequisites["simple-english"]["resolved"],
                str((skills_dir / "simple-english" / "SKILL.md").resolve()),
            )
            self.assertFalse(
                any(
                    entry["path"]
                    == str((skills_dir / "simple-english" / "SKILL.md").resolve())
                    for entry in payload["plan"]
                )
            )
            self.assertEqual(
                {path: path.read_bytes() for path in upstream_files},
                upstream_files,
            )

    def test_repository_launchers_use_disposable_cache_roots(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            environment = os.environ.copy()
            environment["HOME"] = str(home)
            environment.pop("PYTHONPYCACHEPREFIX", None)

            for script in (
                "custom-openspec-install",
                "custom-openspec-init",
                "custom-openspec-grill",
            ):
                result = run_script(script, "--help", environment=environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                for phrase in (PACKAGE_NAME, PROJECT_SHORT_NAME, PROJECT_ALTERNATE_NAME):
                    self.assertIn(phrase, result.stdout)

            default_cache = home / ".cache" / "custom-openspec-workflow"
            self.assertTrue(list(default_cache.rglob("*.pyc")))

            explicit_cache = root / "explicit-cache"
            environment["PYTHONPYCACHEPREFIX"] = str(explicit_cache)
            for script in (
                "custom-openspec-install",
                "custom-openspec-init",
                "custom-openspec-grill",
            ):
                result = run_script(script, "--help", environment=environment)
                self.assertEqual(result.returncode, 0, result.stderr)
                for phrase in (PACKAGE_NAME, PROJECT_SHORT_NAME, PROJECT_ALTERNATE_NAME):
                    self.assertIn(phrase, result.stdout)

            self.assertTrue(list(explicit_cache.rglob("*.pyc")))

    def test_disposable_brownfield_matrix_bootstrap_grill_and_rollback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "brownfield"
            shutil.copytree(FIXTURES / "brownfield", target)

            first = run_script("custom-openspec-init", str(target), "--json")
            self.assertEqual(first.returncode, 0, first.stderr)
            first_payload = json.loads(first.stdout)
            self.assertTrue(first_payload["verifyEnabled"])
            self.assertIn("openspec/config.yaml", "\n".join(first_payload["changedFiles"]))
            self.assertEqual((target / "README.txt").read_text(encoding="utf-8"), "Brownfield fixture content. Keep this file during bootstrap.\n")

            second = run_script("custom-openspec-init", str(target), "--json")
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(json.loads(second.stdout)["changedEntries"], [])

            stage = run_script(
                "custom-openspec-grill",
                "stage",
                "--source",
                str(target / ".grill" / "session-output.md"),
                "--staging-dir",
                str(root / "user-state"),
                "--json",
            )
            self.assertEqual(stage.returncode, 0, stage.stderr)
            session_id = json.loads(stage.stdout)["sessionId"]
            self.assertFalse((target / "grill.md").exists())

            upstream_skills = root / "upstream-skills"
            upstream_skill = upstream_skills / "grill-me" / "SKILL.md"
            upstream_skill.parent.mkdir(parents=True)
            upstream_skill.write_text(
                "---\nname: grill-me\n---\nFixture upstream Grill Me skill.\n",
                encoding="utf-8",
            )
            upstream_before = upstream_skill.read_bytes()
            compatibility = run_script(
                "custom-openspec-grill",
                "compatibility",
                "--source",
                str(target / ".grill" / "session-output.md"),
                "--skills-dir",
                str(upstream_skills),
                "--json",
            )
            self.assertEqual(compatibility.returncode, 0, compatibility.stderr)
            compatibility_payload = json.loads(compatibility.stdout)
            self.assertTrue(compatibility_payload["dependencyAvailable"])
            self.assertTrue(compatibility_payload["requiredSectionsFound"])
            self.assertTrue(compatibility_payload["traceable"])
            self.assertTrue(compatibility_payload["stageSucceeded"])
            self.assertTrue(compatibility_payload["attachmentSucceeded"])
            self.assertTrue(compatibility_payload["repeatedAttachmentIdempotent"])
            self.assertTrue(compatibility_payload["sourceUnchanged"])
            self.assertTrue(compatibility_payload["upstreamUnchanged"])
            self.assertFalse(compatibility_payload["implementationWork"])
            self.assertTrue(compatibility_payload["noImplementationWork"])
            self.assertEqual(upstream_skill.read_bytes(), upstream_before)

            change = target / "openspec" / "changes" / "matrix-change"
            change.mkdir(parents=True)
            attach = run_script(
                "custom-openspec-grill",
                "attach",
                "--root",
                str(target),
                "--change",
                "matrix-change",
                "--session",
                session_id,
                "--staging-dir",
                str(root / "user-state"),
                "--json",
            )
            self.assertEqual(attach.returncode, 0, attach.stderr)
            attached = (change / "grill.md").read_text(encoding="utf-8")
            for section in REQUIRED_SECTIONS:
                self.assertIn(f"## {section}", attached)
            self.assertIn(session_id, attached)
            self.assertIn("supplemental planning context", attached)

            bad_target = root / "bad-policy"
            bad_target.mkdir()
            failed = run_script(
                "custom-openspec-init",
                str(bad_target),
                "--policy",
                str(FIXTURES / "matrix-policy-invalid.yaml"),
                "--json",
            )
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("Rollback completed", failed.stderr)
            self.assertFalse((bad_target / "openspec" / "config.yaml").exists())

            non_stock = root / "non-stock" / "openspec"
            non_stock.mkdir(parents=True)
            non_stock_config = non_stock / "config.yaml"
            non_stock_config.write_text("schema: custom\n", encoding="utf-8")
            refused = run_script("custom-openspec-init", str(non_stock.parent), "--json")
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(non_stock_config.read_text(encoding="utf-8"), "schema: custom\n")

    def test_matrix_covers_the_twelve_lifecycle_scenarios_as_advisory_evidence(self) -> None:
        policy = (PROJECT_ROOT / "src" / "custom_openspec_workflow" / "data" / "openspec-policy.yaml").read_text(encoding="utf-8")
        readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
        records = (FIXTURES / "uat-records.md").read_text(encoding="utf-8")

        self.assertIn("all target needs fit the supported surfaces", (PROJECT_ROOT / "docs" / "compatibility-baseline.md").read_text(encoding="utf-8").lower())
        skill = (PROJECT_ROOT / "src" / "custom_openspec_workflow" / "data" / "custom-openspec-grill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Grill is optional", readme)
        self.assertIn("Skip this skill when normal Explore or Propose already has enough information.", skill)
        self.assertLess(readme.index("/opsx:apply"), readme.index("/opsx:verify"))
        self.assertLess(readme.index("/opsx:verify"), readme.index("/opsx:archive"))
        self.assertIn("HUMAN UAT - PASSED", records)
        self.assertIn("HUMAN UAT - WAIVED BY USER", records)
        self.assertIn("A Verify finding alone does not invalidate completed UAT", policy)
        self.assertIn("reopen only the scenarios", policy)
        self.assertIn("A relevant change also invalidates a waiver", policy)
        self.assertIn("Use a full re-anchor", readme)
        self.assertIn("If Verify is missing, stale, or uncertain", policy)
        self.assertIn("Apply when the plan is correct", policy)
        self.assertIn("Use Update when the plan is incomplete", policy)

    def test_native_openspec_validation_and_status_remain_available(self) -> None:
        validation = subprocess.run(
            ["openspec", "validate", "--all", "--json", "--no-interactive"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(validation.returncode, 0, validation.stderr)
        validation_payload = json.loads(validation.stdout)
        self.assertIsInstance(validation_payload, (dict, list))

        listing = subprocess.run(
            ["openspec", "list", "--json"],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(listing.returncode, 0, listing.stderr)
        listing_payload = json.loads(listing.stdout)
        self.assertTrue(listing_payload["changes"])
        active_change = listing_payload["changes"][0]["name"]

        status = subprocess.run(
            [
                "openspec",
                "status",
                "--change",
                active_change,
                "--json",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(status.returncode, 0, status.stderr)
        status_payload = json.loads(status.stdout)
        self.assertEqual(status_payload["schemaName"], "spec-driven")
        self.assertEqual(status_payload["artifactPaths"]["tasks"]["outputPath"], "tasks.md")

        package_files = [path for path in (PROJECT_ROOT / "src").rglob("*") if path.is_file()]
        self.assertFalse(any(path.name == "verification.md" for path in package_files))
        self.assertFalse(
            any(path.parent.name.startswith("openspec-") and path.name == "SKILL.md" for path in package_files)
        )
