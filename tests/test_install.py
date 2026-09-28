from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from custom_openspec_workflow import (
    PACKAGE_NAME,
    PROJECT_ALTERNATE_NAME,
    PROJECT_IDENTITY,
    PROJECT_SHORT_NAME,
)
from custom_openspec_workflow.install import (
    InstallConflictError,
    build_install_plan,
    build_uninstall_plan,
    hash_file,
    install_user,
    main,
    uninstall_user,
)


PROJECT_ROOT = Path(__file__).parents[1]
SOURCE_PACKAGE = PROJECT_ROOT / "src" / "custom_openspec_workflow"


class TTYInput(io.StringIO):
    def isatty(self) -> bool:
        return True


class InstallTests(unittest.TestCase):
    def layout(self, root: Path) -> dict[str, Path]:
        return {
            "skills_dir": root / "skills",
            "bin_dir": root / "bin",
            "install_dir": root / "install",
        }

    def install(self, root: Path, *, source_root: Path = SOURCE_PACKAGE) -> dict:
        return install_user(**self.layout(root), source_root=source_root)

    def cli_arguments(self, root: Path, *extra: str) -> list[str]:
        layout = self.layout(root)
        return [
            "--skills-dir",
            str(layout["skills_dir"]),
            "--bin-dir",
            str(layout["bin_dir"]),
            "--install-dir",
            str(layout["install_dir"]),
            "--source-root",
            str(SOURCE_PACKAGE),
            *extra,
        ]

    def run_cli(
        self,
        arguments: list[str],
        *,
        input_text: str = "",
        interactive: bool = False,
    ) -> tuple[int, str, str]:
        stdin = TTYInput(input_text) if interactive else io.StringIO(input_text)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            patch("sys.stdin", stdin),
            redirect_stdout(stdout),
            redirect_stderr(stderr),
        ):
            return_code = main(arguments)
        return return_code, stdout.getvalue(), stderr.getvalue()

    def managed_paths(self, root: Path) -> list[Path]:
        manifest_path = self.layout(root)["install_dir"] / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return [Path(path) for path in manifest["files"]] + [manifest_path]

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

    def test_install_plan_reports_available_prerequisites_in_selected_skills_dir(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            upstream = layout["skills_dir"] / "grill-me" / "SKILL.md"
            upstream.parent.mkdir(parents=True)
            upstream.write_text(
                "---\nname: grill-me\n---\nUpstream Grill Me skill.\n",
                encoding="utf-8",
            )
            simple_english = layout["skills_dir"] / "simple-english" / "SKILL.md"
            simple_english.parent.mkdir(parents=True)
            simple_english.write_text(
                "---\nname: simple-english\n---\nUpstream Simple English skill.\n",
                encoding="utf-8",
            )
            openspec = root / "openspec"

            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=openspec,
            ):
                plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)

            prerequisites = {item.name: item for item in plan.prerequisites}
            self.assertEqual(prerequisites["grill-me"].status, "available")
            self.assertEqual(prerequisites["grill-me"].checked, str(layout["skills_dir"].resolve()))
            self.assertEqual(prerequisites["grill-me"].resolved, str(upstream.resolve()))
            self.assertEqual(prerequisites["grill-me"].value, "surfaces unclear intent, hidden constraints, decisions, tradeoffs, non-goals, and open questions before planning.")
            self.assertEqual(prerequisites["simple-english"].status, "available")
            self.assertEqual(prerequisites["simple-english"].checked, str(layout["skills_dir"].resolve()))
            self.assertEqual(prerequisites["simple-english"].resolved, str(simple_english.resolve()))
            self.assertEqual(prerequisites["simple-english"].value, "helps write clear documentation with short sentences, active voice, and consistent terms.")
            self.assertEqual(prerequisites["openspec"].status, "available")
            self.assertEqual(prerequisites["openspec"].resolved, str(openspec.resolve()))
            self.assertFalse(plan.conflicts)
            self.assertNotIn(upstream.resolve(), plan.expected_files)
            self.assertNotIn(str(upstream.resolve()), plan.manifest_data["files"])

    def test_install_plan_reports_missing_prerequisites_without_writes_or_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)

            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)

            prerequisites = {item.name: item for item in plan.prerequisites}
            grill_me = prerequisites["grill-me"]
            simple_english = prerequisites["simple-english"]
            openspec = prerequisites["openspec"]
            self.assertEqual(grill_me.status, "missing")
            self.assertEqual(grill_me.checked, str(layout["skills_dir"].resolve()))
            self.assertIn("satya-janghu/agent-skills", grill_me.remediation)
            self.assertIn("skills/grill-me", grill_me.remediation)
            self.assertIn("README", grill_me.remediation)
            self.assertEqual(simple_english.status, "missing")
            self.assertEqual(simple_english.checked, str(layout["skills_dir"].resolve()))
            self.assertIn("AminBlg/SimpleEnglish", simple_english.remediation)
            self.assertIn("skills/simple-english", simple_english.remediation)
            self.assertIn("README", simple_english.remediation)
            self.assertEqual(simple_english.value, "helps write clear documentation with short sentences, active voice, and consistent terms.")
            self.assertEqual(openspec.status, "missing")
            self.assertEqual(openspec.checked, "openspec on PATH")
            for phrase in (
                "npm install -g @fission-ai/openspec@latest",
                "openspec --version",
                "--openspec-executable /path/to/openspec",
                "workflow cannot function until OpenSpec is installed",
                "does not install OpenSpec",
            ):
                self.assertIn(phrase, openspec.remediation)
            self.assertFalse(plan.conflicts)
            self.assertFalse(root.joinpath("skills").exists())
            self.assertFalse(root.joinpath("bin").exists())
            self.assertFalse(root.joinpath("install").exists())
            self.assertFalse(
                any(path.name == "grill-me" for path in plan.expected_files)
            )

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
            self.assertTrue(init_text.startswith("#!/bin/sh\n"))
            self.assertIn('if [ "${PYTHONPYCACHEPREFIX+x}" != x ]', init_text)
            self.assertIn("export PYTHONPYCACHEPREFIX", init_text)
            self.assertIn("install_root = sys.argv.pop(1)", init_text)
            self.assertIn("sys.path.insert(0, install_root)", init_text)
            self.assertLess(init_text.index("export PYTHONPYCACHEPREFIX"), init_text.index("exec python3"))
            self.assertIn("from custom_openspec_workflow.bootstrap import main", init_text)
            self.assertIn("from custom_openspec_workflow.grill_cli import main", grill_text)

            subprocess_environment = os.environ.copy()
            subprocess_environment.pop("PYTHONPYCACHEPREFIX", None)
            subprocess_environment["HOME"] = str(home)
            for wrapper in (init_wrapper, grill_wrapper):
                result = subprocess.run(
                    [str(wrapper), "--help"],
                    env=subprocess_environment,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_installed_helper_uses_default_cache_without_package_local_bytecode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            with patch.dict(os.environ, {"HOME": str(home)}, clear=False):
                os.environ.pop("PYTHONPYCACHEPREFIX", None)
                self.install(root)

            environment = os.environ.copy()
            environment["HOME"] = str(home)
            environment.pop("PYTHONPYCACHEPREFIX", None)
            result = subprocess.run(
                [str(self.layout(root)["bin_dir"] / "custom-openspec-grill"), "--help"],
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            installed_package = self.layout(root)["install_dir"] / "custom_openspec_workflow"
            self.assertFalse(list(installed_package.rglob("__pycache__")))
            cache_root = home / ".cache" / "custom-openspec-workflow"
            self.assertTrue(list(cache_root.rglob("*.pyc")))

    def test_explicit_cache_is_unowned_and_survives_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "home"
            with patch.dict(os.environ, {"HOME": str(home)}, clear=False):
                os.environ.pop("PYTHONPYCACHEPREFIX", None)
                self.install(root)

            explicit_cache = root / "selected-cache"
            environment = os.environ.copy()
            environment["HOME"] = str(home)
            environment["PYTHONPYCACHEPREFIX"] = str(explicit_cache)
            result = subprocess.run(
                [str(self.layout(root)["bin_dir"] / "custom-openspec-init"), "--help"],
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            cache_files = list(explicit_cache.rglob("*.pyc"))
            self.assertTrue(cache_files)
            self.assertFalse((home / ".cache" / "custom-openspec-workflow").exists())

            layout = self.layout(root)
            manifest_path = layout["install_dir"] / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_paths = [Path(path) for path in manifest["files"]]
            self.assertFalse(any(path.is_relative_to(explicit_cache) for path in manifest_paths))

            plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)
            self.assertFalse(plan.conflicts)
            self.assertFalse(
                any(
                    entry.path == explicit_cache or explicit_cache in entry.path.parents
                    for entry in plan.entries
                )
            )

            payload = uninstall_user(**layout)

            self.assertEqual(payload["preserved"], [])
            self.assertFalse(manifest_path.exists())
            self.assertTrue(explicit_cache.is_dir())
            self.assertEqual(cache_files, [path for path in explicit_cache.rglob("*.pyc")])

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

    def test_install_plan_enumerates_files_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)

            expected_paths = set(plan.expected_files) | {plan.manifest_path}
            planned_paths = {entry.path for entry in plan.entries}
            self.assertTrue(expected_paths <= planned_paths)
            self.assertTrue(
                all(
                    any(entry.path == path and entry.operation == "create" for entry in plan.entries)
                    for path in expected_paths
                )
            )
            self.assertTrue(plan.manifest_data)
            self.assertEqual(
                set(plan.manifest_data["files"]),
                {str(path) for path in plan.expected_files},
            )
            self.assertFalse(layout["skills_dir"].exists())
            self.assertFalse(layout["bin_dir"].exists())
            self.assertFalse(layout["install_dir"].exists())

    def test_json_plan_orders_extra_path_conflicts_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            package_extra = layout["install_dir"] / "custom_openspec_workflow" / "extra.py"
            skill_extra = layout["skills_dir"] / "custom-openspec-grill" / "extra.md"
            for path in (package_extra, skill_extra):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("user-owned content\n", encoding="utf-8")

            command = [
                str(PROJECT_ROOT / "scripts" / "custom-openspec-install"),
                *self.cli_arguments(root, "--json"),
            ]
            plans = []
            for seed in ("1", "2"):
                result = subprocess.run(
                    command,
                    env={**os.environ, "PYTHONHASHSEED": seed},
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertEqual(result.stderr, "")
                plans.append(json.loads(result.stdout)["plan"])

            self.assertEqual(plans[0], plans[1])
            conflict_paths = [
                entry["path"]
                for entry in plans[0]
                if entry["operation"] == "conflict"
            ]
            self.assertEqual(conflict_paths, [str(package_extra), str(skill_extra)])

    def test_fresh_empty_install_records_hashes_and_modes_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = build_install_plan(**self.layout(root), source_root=SOURCE_PACKAGE)
            self.assertFalse(plan.conflicts)
            self.install(root)
            layout = self.layout(root)
            manifest_path = layout["install_dir"] / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

            self.assertEqual(manifest["format"], "custom-openspec-workflow-install")
            self.assertNotIn(str(manifest_path), manifest["files"])
            for raw_path, record in manifest["files"].items():
                path = Path(raw_path)
                self.assertEqual(record["sha256"], hash_file(path))
                self.assertEqual(record["mode"], stat.S_IMODE(path.stat().st_mode))
            self.assertEqual(
                stat.S_IMODE((layout["bin_dir"] / "custom-openspec-init").stat().st_mode),
                0o755,
            )
            self.assertEqual(
                stat.S_IMODE((layout["bin_dir"] / "custom-openspec-grill").stat().st_mode),
                0o755,
            )

    def test_complete_prepopulated_target_without_manifest_blocks_install(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            expected_plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)
            for item in expected_plan.expected_files.values():
                item.path.parent.mkdir(parents=True, exist_ok=True)
                item.path.write_bytes(item.data)
                item.path.chmod(item.mode)

            before = {
                item.path: item.path.read_bytes()
                for item in expected_plan.expected_files.values()
            }
            plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)

            self.assertTrue(plan.is_blocked)
            for path in expected_plan.expected_files:
                self.assertTrue(
                    any(
                        entry.path == path and entry.operation == "conflict"
                        for entry in plan.entries
                    )
                )
            with self.assertRaises(InstallConflictError):
                install_user(**layout, source_root=SOURCE_PACKAGE)

            self.assertEqual(
                {path: path.read_bytes() for path in before},
                before,
            )
            self.assertFalse((layout["install_dir"] / "manifest.json").exists())

    def test_repeated_install_replaces_unchanged_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            shutil.copytree(SOURCE_PACKAGE, source)
            self.install(root, source_root=source)

            upgraded = source / "__init__.py"
            upgraded.write_bytes(upgraded.read_bytes() + b"\nUPGRADED = True\n")
            plan = build_install_plan(**self.layout(root), source_root=source)
            target = self.layout(root)["install_dir"] / "custom_openspec_workflow" / "__init__.py"
            self.assertTrue(
                any(entry.path == target and entry.operation == "replace" for entry in plan.entries)
            )

            payload = install_user(**self.layout(root), source_root=source)

            self.assertEqual(payload["status"], "completed")
            self.assertEqual(target.read_bytes(), upgraded.read_bytes())
            self.assertFalse(payload["conflicts"])

    def test_unmanaged_existing_path_blocks_install_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            layout["bin_dir"].mkdir()
            unmanaged = layout["bin_dir"] / "custom-openspec-init"
            unmanaged.write_text("user-owned wrapper\n", encoding="utf-8")
            before = unmanaged.read_bytes()

            plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)
            self.assertTrue(any(str(unmanaged) in conflict for conflict in plan.conflicts))
            with self.assertRaises(InstallConflictError):
                install_user(**layout, source_root=SOURCE_PACKAGE)

            self.assertEqual(unmanaged.read_bytes(), before)
            self.assertFalse(layout["install_dir"].exists())
            self.assertFalse(layout["skills_dir"].exists())
            self.assertEqual(sorted(path.name for path in layout["bin_dir"].iterdir()), [unmanaged.name])

    def test_modified_managed_file_blocks_install_without_replacing_it(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root)
            layout = self.layout(root)
            target = layout["install_dir"] / "custom_openspec_workflow" / "install.py"
            manifest = layout["install_dir"] / "manifest.json"
            target.write_text("user modification\n", encoding="utf-8")
            before_manifest = manifest.read_bytes()

            plan = build_install_plan(**layout, source_root=SOURCE_PACKAGE)
            self.assertTrue(any(entry.path == target and entry.operation == "conflict" for entry in plan.entries))
            with self.assertRaises(InstallConflictError):
                install_user(**layout, source_root=SOURCE_PACKAGE)

            self.assertEqual(target.read_text(encoding="utf-8"), "user modification\n")
            self.assertEqual(manifest.read_bytes(), before_manifest)

    def test_missing_manifest_blocks_uninstall_without_removing_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root)
            layout = self.layout(root)
            managed = self.managed_paths(root)
            (layout["install_dir"] / "manifest.json").unlink()
            before = {path: path.read_bytes() for path in managed if path.is_file()}

            plan = build_uninstall_plan(**layout)
            self.assertTrue(plan.is_blocked)
            with self.assertRaises(InstallConflictError):
                uninstall_user(**layout)

            self.assertEqual(
                {path: path.read_bytes() for path in before if path.exists()},
                {path: data for path, data in before.items()},
            )

    def test_declined_cli_install_displays_plan_before_prompt_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root),
                    input_text="n\n",
                    interactive=True,
                )

            self.assertEqual(return_code, 0)
            self.assertEqual(stderr, "")
            self.assertLess(stdout.index("create:"), stdout.index("Continue with package installation?"))
            self.assertLess(stdout.index("warning:"), stdout.index("Continue with package installation?"))
            self.assertIn("satya-janghu/agent-skills", stdout)
            self.assertIn(
                "value: surfaces unclear intent, hidden constraints, decisions, tradeoffs, non-goals, and open questions before planning.",
                stdout,
            )
            self.assertIn(
                "value: helps write clear documentation with short sentences, active voice, and consistent terms.",
                stdout,
            )
            self.assertLess(
                stdout.index("warning: Install satya-janghu/agent-skills"),
                stdout.index("warning: Install AminBlg/SimpleEnglish"),
            )
            self.assertIn("Continue with package installation?", stdout)
            self.assertLess(stdout.index("warning:"), stdout.index("Continue with package installation?"))
            self.assertIn("cancelled", stdout)
            self.assertFalse(self.layout(root)["install_dir"].exists())
            self.assertFalse(self.layout(root)["skills_dir"].exists())
            self.assertFalse(self.layout(root)["bin_dir"].exists())

    def test_human_plan_result_and_refusal_show_project_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            return_code, stdout, stderr = self.run_cli(
                self.cli_arguments(root, "--dry-run"),
            )

            self.assertEqual(return_code, 0, stderr)
            for phrase in (PACKAGE_NAME, PROJECT_SHORT_NAME, PROJECT_ALTERNATE_NAME):
                self.assertIn(phrase, stdout)

            return_code, stdout, stderr = self.run_cli(
                self.cli_arguments(root, "--host", "claude", "--dry-run"),
            )

            self.assertEqual(return_code, 2)
            self.assertEqual(stdout, "")
            self.assertIn(PROJECT_IDENTITY, stderr)

    def test_json_plan_and_result_keep_human_branding_out(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--json", "--yes"),
                )

            self.assertEqual(return_code, 0, stderr)
            result = json.loads(stdout)
            plan = json.loads(stderr)
            self.assertIn("operation", result)
            self.assertIn("plan", result)
            self.assertIn("prerequisites", result)
            self.assertIn("operation", plan)
            for output in (stdout, stderr):
                self.assertNotIn(PROJECT_SHORT_NAME, output)
                self.assertNotIn(PROJECT_ALTERNATE_NAME, output)
                self.assertNotIn(PROJECT_IDENTITY, output)

    def test_yes_install_keeps_missing_prerequisite_warning_and_applies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--yes"),
                )

            self.assertEqual(return_code, 0, stderr)
            self.assertIn("warning:", stdout)
            self.assertIn("completed", stdout)
            self.assertTrue((self.layout(root)["install_dir"] / "manifest.json").is_file())

    def test_declined_cli_uninstall_displays_plan_before_prompt_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root)
            managed = self.managed_paths(root)
            before = {path: path.read_bytes() for path in managed}

            return_code, stdout, stderr = self.run_cli(
                self.cli_arguments(root, "--uninstall"),
                input_text="n\n",
                interactive=True,
            )

            self.assertEqual(return_code, 0)
            self.assertEqual(stderr, "")
            self.assertLess(stdout.index("remove:"), stdout.index("Apply this uninstall operation?"))
            self.assertIn("cancelled", stdout)
            self.assertEqual(
                {path: path.read_bytes() for path in managed},
                before,
            )

    def test_cli_yes_aliases_apply_install_and_uninstall_without_prompt(self) -> None:
        for alias in ("-y", "--yes"):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, alias),
                )
                self.assertEqual(return_code, 0, stderr)
                self.assertNotIn("Apply this install operation?", stdout)
                self.assertTrue((self.layout(root)["install_dir"] / "manifest.json").is_file())

                uninstall_args = self.cli_arguments(root, "--uninstall", alias)
                return_code, stdout, stderr = self.run_cli(uninstall_args)
                self.assertEqual(return_code, 0, stderr)
                self.assertNotIn("Apply this uninstall operation?", stdout)
                self.assertFalse((self.layout(root)["install_dir"] / "manifest.json").exists())

    def test_json_cli_emits_plan_before_apply_and_keeps_result_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--json", "--yes"),
                )

            self.assertEqual(return_code, 0, stderr)
            result = json.loads(stdout)
            plan = json.loads(stderr)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(plan["operation"], "install")
            self.assertEqual(plan["plan"], result["plan"])
            self.assertEqual(plan["prerequisites"], result["prerequisites"])
            self.assertEqual(
                {item["name"] for item in result["prerequisites"]},
                {"grill-me", "simple-english", "openspec"},
            )
            missing = {
                item["name"]: item
                for item in result["prerequisites"]
                if item["status"] == "missing"
            }
            self.assertIn("grill-me", missing)
            self.assertIn("satya-janghu/agent-skills", missing["grill-me"]["remediation"])
            self.assertIn("AminBlg/SimpleEnglish", missing["simple-english"]["remediation"])
            self.assertEqual(
                missing["simple-english"]["value"],
                "helps write clear documentation with short sentences, active voice, and consistent terms.",
            )
            self.assertEqual(
                result["prerequisites"][0]["value"],
                "surfaces unclear intent, hidden constraints, decisions, tradeoffs, non-goals, and open questions before planning.",
            )
            self.assertTrue(result["plan"])

    def test_json_cli_confirmation_plan_precedes_prompt_and_cancellation_result(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--json"),
                    input_text="n\n",
                    interactive=True,
                )

            self.assertEqual(return_code, 0)
            result = json.loads(stdout)
            self.assertEqual(result["status"], "cancelled")
            self.assertLess(
                stderr.index('"plan"'),
                stderr.index("Continue with package installation?"),
            )
            self.assertFalse(self.layout(root)["install_dir"].exists())

    def test_json_dry_run_returns_plan_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--json", "--dry-run"),
                )

            self.assertEqual(return_code, 0, stderr)
            result = json.loads(stdout)
            self.assertEqual(result["status"], "dry-run")
            self.assertTrue(result["plan"])
            self.assertEqual(len(result["prerequisites"]), 3)
            self.assertTrue(all(item["status"] == "missing" for item in result["prerequisites"]))
            values = {item["name"]: item["value"] for item in result["prerequisites"]}
            self.assertEqual(
                values["grill-me"],
                "surfaces unclear intent, hidden constraints, decisions, tradeoffs, non-goals, and open questions before planning.",
            )
            self.assertEqual(
                values["simple-english"],
                "helps write clear documentation with short sentences, active voice, and consistent terms.",
            )
            self.assertEqual(stderr, "")
            self.assertFalse(self.layout(root)["install_dir"].exists())
            self.assertFalse(self.layout(root)["skills_dir"].exists())
            self.assertFalse(self.layout(root)["bin_dir"].exists())

    def test_human_and_json_dry_runs_show_values_for_available_optional_skills(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            for name in ("grill-me", "simple-english"):
                skill = layout["skills_dir"] / name / "SKILL.md"
                skill.parent.mkdir(parents=True, exist_ok=True)
                skill.write_text(f"---\nname: {name}\n---\n", encoding="utf-8")

            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=root / "openspec",
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--dry-run"),
                )
            self.assertEqual(return_code, 0, stderr)
            self.assertIn(
                "value: surfaces unclear intent, hidden constraints, decisions, tradeoffs, non-goals, and open questions before planning.",
                stdout,
            )
            self.assertIn(
                "value: helps write clear documentation with short sentences, active voice, and consistent terms.",
                stdout,
            )
            self.assertNotIn("warning: Install satya-janghu/agent-skills", stdout)
            self.assertNotIn("warning: Install AminBlg/SimpleEnglish", stdout)
            self.assertEqual(stderr, "")

            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=root / "openspec",
            ):
                return_code, stdout, stderr = self.run_cli(
                    self.cli_arguments(root, "--json", "--dry-run"),
                )
            self.assertEqual(return_code, 0, stderr)
            payload = json.loads(stdout)
            prerequisites = {item["name"]: item for item in payload["prerequisites"]}
            self.assertEqual(prerequisites["grill-me"]["status"], "available")
            self.assertEqual(prerequisites["simple-english"]["status"], "available")
            self.assertTrue(prerequisites["grill-me"]["value"])
            self.assertTrue(prerequisites["simple-english"]["value"])
            self.assertEqual(stderr, "")

    def test_noninteractive_cli_requires_explicit_confirmation_bypass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            return_code, stdout, stderr = self.run_cli(
                self.cli_arguments(root, "--json"),
            )

            self.assertEqual(return_code, 2)
            result = json.loads(stdout)
            self.assertEqual(result["status"], "blocked")
            self.assertIn("requires explicit -y or --yes", result["error"])
            self.assertIn('"plan"', stderr)
            self.assertFalse(self.layout(root)["install_dir"].exists())

    def test_uninstall_removes_unchanged_files_and_preserves_unrelated_data(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root)
            layout = self.layout(root)
            unrelated = layout["install_dir"] / "user-data.txt"
            unrelated.write_text("keep me\n", encoding="utf-8")
            grill_session = layout["install_dir"] / "grill" / "session-output.md"
            grill_session.parent.mkdir()
            grill_session.write_text("staging data\n", encoding="utf-8")
            upstream_skill = layout["skills_dir"] / "grill-me" / "SKILL.md"
            upstream_skill.parent.mkdir()
            upstream_skill.write_text("upstream skill\n", encoding="utf-8")
            managed = self.managed_paths(root)

            payload = uninstall_user(**layout)

            self.assertTrue(payload["uninstalled"])
            self.assertEqual(payload["preserved"], [])
            self.assertTrue(all(not path.exists() for path in managed))
            self.assertTrue(layout["install_dir"].is_dir())
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep me\n")
            self.assertEqual(grill_session.read_text(encoding="utf-8"), "staging data\n")
            self.assertEqual(upstream_skill.read_text(encoding="utf-8"), "upstream skill\n")

    def test_uninstall_skips_missing_prerequisite_checks_and_preserves_upstream_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            with patch(
                "custom_openspec_workflow.install.executable_in_path",
                return_value=None,
            ):
                self.install(root)

            upstream_skill = layout["skills_dir"] / "grill-me" / "SKILL.md"
            upstream_skill.parent.mkdir(parents=True)
            upstream_skill.write_text("upstream skill\n", encoding="utf-8")
            unrelated = layout["install_dir"] / "user-data.txt"
            unrelated.write_text("keep me\n", encoding="utf-8")

            with (
                patch(
                    "custom_openspec_workflow.install.executable_in_path",
                    return_value=None,
                ) as executable_lookup,
                patch(
                    "custom_openspec_workflow.install.discover_grill_me_skill",
                    return_value=None,
                ) as grill_lookup,
                patch(
                    "custom_openspec_workflow.install.discover_simple_english_skill",
                    return_value=None,
                ) as simple_english_lookup,
            ):
                plan = build_uninstall_plan(**layout)
                payload = uninstall_user(**layout)

            executable_lookup.assert_not_called()
            grill_lookup.assert_not_called()
            simple_english_lookup.assert_not_called()
            self.assertEqual(plan.prerequisites, [])
            self.assertEqual(payload["prerequisites"], [])
            self.assertEqual(upstream_skill.read_text(encoding="utf-8"), "upstream skill\n")
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "keep me\n")

    def test_uninstall_preserves_modified_managed_file_and_removes_others(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.install(root)
            layout = self.layout(root)
            modified = layout["install_dir"] / "custom_openspec_workflow" / "install.py"
            modified.write_text("user edit\n", encoding="utf-8")
            unchanged = layout["install_dir"] / "custom_openspec_workflow" / "__init__.py"

            payload = uninstall_user(**layout)

            self.assertIn(str(modified), payload["preserved"])
            self.assertEqual(modified.read_text(encoding="utf-8"), "user edit\n")
            self.assertFalse(unchanged.exists())
            self.assertFalse((layout["skills_dir"] / "custom-openspec-grill" / "SKILL.md").exists())
            self.assertFalse((layout["bin_dir"] / "custom-openspec-init").exists())
            self.assertFalse((layout["install_dir"] / "manifest.json").exists())

    def test_manifest_free_uninstall_refuses_to_guess_and_preserves_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            layout = self.layout(root)
            package_file = layout["install_dir"] / "custom_openspec_workflow" / "install.py"
            skill_file = layout["skills_dir"] / "custom-openspec-grill" / "SKILL.md"
            wrapper = layout["bin_dir"] / "custom-openspec-init"
            for path in (package_file, skill_file, wrapper):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("user-owned content\n", encoding="utf-8")
            before = {path: path.read_bytes() for path in (package_file, skill_file, wrapper)}

            plan = build_uninstall_plan(**layout)
            self.assertTrue(plan.is_blocked)
            with self.assertRaises(InstallConflictError):
                uninstall_user(**layout)

            self.assertEqual(
                {path: path.read_bytes() for path in before},
                before,
            )

    def test_uninstall_does_not_modify_repository_or_global_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repository = root / "repository"
            repository_files = {
                repository / "README.md": b"repository sentinel\n",
                repository / "openspec" / "config.yaml": b"schema: spec-driven\n",
                repository / ".agents" / "skills" / "custom" / "SKILL.md": b"repo skill\n",
                repository / "src" / "sentinel.py": b"SENTINEL = True\n",
            }
            global_config = root / "global-openspec-config.json"
            repository_files[global_config] = b'{"profile":"core"}\n'
            for path, content in repository_files.items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)

            self.install(root)
            uninstall_user(**self.layout(root))

            self.assertEqual(
                {path: path.read_bytes() for path in repository_files},
                repository_files,
            )

    def test_upgrade_removes_old_unchanged_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            shutil.copytree(SOURCE_PACKAGE, source)
            obsolete = source / "obsolete_module.py"
            obsolete.write_text("OBSOLETE = True\n", encoding="utf-8")
            self.install(root, source_root=source)
            target = self.layout(root)["install_dir"] / "custom_openspec_workflow" / obsolete.name
            self.assertTrue(target.exists())

            obsolete.unlink()
            payload = install_user(**self.layout(root), source_root=source)
            manifest = json.loads(
                (self.layout(root)["install_dir"] / "manifest.json").read_text(encoding="utf-8")
            )

            self.assertIn(str(target), payload["changedFiles"])
            self.assertFalse(target.exists())
            self.assertNotIn(str(target), manifest["files"])
