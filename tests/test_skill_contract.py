from __future__ import annotations

from pathlib import Path
import unittest

import yaml

from custom_openspec_workflow import (
    PACKAGE_NAME,
    PROJECT_ALTERNATE_NAME,
    PROJECT_SHORT_NAME,
)
from custom_openspec_workflow.host import UnsupportedHostError, discover_host


class SkillContractTests(unittest.TestCase):
    def package_file(self, relative_path: str) -> str:
        root = Path(__file__).parents[1]
        return (root / "src" / "custom_openspec_workflow" / "data" / relative_path).read_text(
            encoding="utf-8"
        )

    def test_adapter_delegates_without_copying_question_logic(self) -> None:
        text = self.package_file("custom-openspec-grill/SKILL.md")
        self.assertIn("name: custom-openspec-grill", text)
        self.assertIn("upstream `grill-me` skill", text)
        self.assertIn("~/.agents/skills", text)
        self.assertIn("grill-me/SKILL.md", text)
        self.assertIn("satya-janghu/agent-skills", text)
        self.assertIn("skills/grill-me", text)
        self.assertIn("package README", text)
        self.assertIn("Grill cannot run until `grill-me` is installed", text)
        self.assertIn("normal OpenSpec Explore and Propose work remains available", text)
        self.assertNotIn("Question lenses", text)
        self.assertNotIn("Core loop", text)
        self.assertNotIn("one question at a time", text)
        self.assertNotIn("relentlessly", text)

    def test_identity_is_present_in_static_surfaces_without_renaming_skill(self) -> None:
        root = Path(__file__).parents[1]
        skill = self.package_file("custom-openspec-grill/SKILL.md")
        readme = (root / "README.md").read_text(encoding="utf-8")
        metadata = (root / "pyproject.toml").read_text(encoding="utf-8")

        self.assertIn("name: custom-openspec-grill", skill)
        self.assertIn("official package name", skill)
        self.assertIn("short name", readme)
        for surface in (skill, readme, metadata):
            self.assertIn(PACKAGE_NAME, surface)
            self.assertIn(PROJECT_SHORT_NAME, surface)
            self.assertIn(PROJECT_ALTERNATE_NAME, surface)

    def test_skill_preflights_sources_and_preserves_read_only_snapshots(self) -> None:
        text = self.package_file("custom-openspec-grill/SKILL.md")

        self.assertIn("git -C <repository> check-ignore -q -- .grill/", text)
        self.assertIn("add `.grill/` to `<repository>/.gitignore`", text)
        self.assertIn("Do not edit `.gitignore`", text)
        self.assertIn("Do not invoke Grill Me, stage a source, or attach a session", text)
        self.assertIn("read-only snapshot", text)
        self.assertIn("Do not edit or delete the source", text)
        self.assertLess(text.index("check-ignore -q"), text.index("## Delegate to Grill Me"))

    def test_skill_stages_exact_source_and_retains_pending_handoff(self) -> None:
        text = self.package_file("custom-openspec-grill/SKILL.md")

        self.assertIn("use the exact source path in its result", text)
        self.assertIn("generated filename slug", text)
        self.assertIn("newest timestamp", text)
        self.assertIn("exact-source-path", text)
        self.assertIn(
            "custom-openspec-grill stage " + "\\\n" + "  --source <exact-source-path> " + "\\\n" + "  --json",
            text,
        )
        self.assertIn("sourcePath", text)
        self.assertIn("sessionId", text)
        self.assertIn("stagingDir", text)
        self.assertIn("pending handoff", text)
        self.assertIn("exactly one plausible source", text)
        self.assertIn("more than one plausible source", text)
        self.assertIn("ask the user to select the source", text)
        self.assertLess(text.index("use the exact source path"), text.index("custom-openspec-grill stage"))

    def test_skill_attaches_before_propose_and_handles_conflicts(self) -> None:
        text = self.package_file("custom-openspec-grill/SKILL.md")

        self.assertIn("--root <repository>", text)
        self.assertIn("--change <change-name>", text)
        self.assertIn("--session <session-id>", text)
        self.assertIn("If exactly one applicable named change exists, select it automatically", text)
        self.assertIn("more than one applicable named change exists", text)
        self.assertIn("Do not pass `--replace` or `--combine`", text)
        self.assertIn("before Propose writes", text)
        self.assertIn("same session is already complete", text)
        self.assertIn("latest explicit user decision takes precedence", text)

    def test_skill_documents_the_recommended_order_and_native_explore_limit(self) -> None:
        text = self.package_file("custom-openspec-grill/SKILL.md")

        self.assertIn("Use OpenSpec Explore for discussion and repository investigation", text)
        self.assertIn("Grill Me is optional", text)
        self.assertIn("normal writer of the initial planning artifacts", text)
        self.assertIn("high uncertainty", text)
        self.assertIn("cannot block native Explore", text)
        self.assertIn("Do not rewrite that artifact automatically", text)
        self.assertIn("The user can use OpenSpec Update", text)

    def test_policy_preserves_supported_operations_and_excludes_explore_guidance(self) -> None:
        policy_text = self.package_file("openspec-policy.yaml")
        policy = yaml.safe_load(policy_text)

        self.assertIn("proposal", policy["rules"])
        self.assertIn("specs", policy["rules"])
        self.assertIn("design", policy["rules"])
        self.assertIn("tasks", policy["rules"])
        for artifact_id in ("proposal", "specs", "design", "tasks"):
            guidance = "\n".join(policy["rules"][artifact_id])
            self.assertIn("complete any pending Grill handoff", guidance)
            self.assertIn("supplemental planning input", guidance)
            self.assertIn("latest explicit user decision takes precedence", guidance)
            self.assertIn("cannot prevent native Explore artifact writes", guidance)
        self.assertIn("apply", policy["operations"])
        self.assertIn("archive", policy["operations"])
        self.assertNotIn("explore", policy["operations"])

    def test_policy_limits_commit_guidance_to_archive_or_explicit_pause(self) -> None:
        policy = yaml.safe_load(self.package_file("openspec-policy.yaml"))
        apply_guidance = "\n".join(policy["operations"]["apply"]["guidance"])
        archive_guidance = "\n".join(policy["operations"]["archive"]["guidance"])

        self.assertIn("Git commit guidance is advisory", apply_guidance)
        self.assertIn(
            "During normal Explore, Propose, Apply, Update, Verify, UAT, and pre-Archive work, do not recommend a Git commit.",
            apply_guidance,
        )
        self.assertIn("docs(openspec): checkpoint <change-name>", apply_guidance)
        self.assertIn("Do not mark unfinished tasks complete", apply_guidance)
        self.assertIn("without successful Archive or an explicit user pause", apply_guidance)
        self.assertIn("only after native Archive completes successfully", archive_guidance)
        self.assertIn("while Archive is running", archive_guidance)
        self.assertIn("after Archive reports failure", archive_guidance)
        self.assertIn("strongly recommend the relevant Git commits", archive_guidance)

    def test_policy_documents_separable_git_commit_safety_guidance(self) -> None:
        policy = yaml.safe_load(self.package_file("openspec-policy.yaml"))
        guidance = "\n".join(policy["operations"]["archive"]["guidance"])

        for phrase in (
            "separate commits for the archived OpenSpec content and the intended non-OpenSpec outcome",
            "one outcome commit only when intended non-OpenSpec changes exist",
            "explicit file lists for both commits",
            "no unrelated worktree paths",
            "git commit --only",
            "`type(scope): subject`",
            "Describe the outcome, not the process",
            "`pre-commit` and `commit-msg` hooks normally",
            "does not recommend `--no-verify` by default",
            "`git revert --no-commit`",
            "recommend a squash merge without requiring it",
            "suggest `git init`",
            "Do not run `git init` automatically",
            "change Git state automatically",
        ):
            self.assertIn(phrase, guidance)

        for branch in ("main", "master", "trunk", "staging", "develop", "development", "dev"):
            self.assertIn(f"`{branch}`", guidance)
        self.assertIn("common protected-branch candidates", guidance)
        self.assertIn("Do not claim that a branch is protected or block the commit", guidance)

    def test_readme_documents_the_grill_handoff_and_retention_rules(self) -> None:
        root = Path(__file__).parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")

        for phrase in (
            "Explore discussion",
            "Grill-first",
            "high uncertainty",
            "pending handoff",
            "exact source path",
            "more than one plausible source",
            "more than one applicable named change",
            "read-only snapshot",
            "latest explicit user decision",
            "openspec/changes/archive/<date>-<change>/grill.md",
            "manual user action",
            "./scripts/custom-openspec-install",
        ):
            self.assertIn(phrase, readme)

    def test_readme_documents_git_lifecycle_commit_boundaries(self) -> None:
        root = Path(__file__).parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        lifecycle = " ".join(readme[readme.index("## Git lifecycle guidance") :].split())

        self.assertLess(readme.index("## Archive"), readme.index("## Git lifecycle guidance"))
        self.assertLess(readme.index("## Git lifecycle guidance"), readme.index("## Re-anchor during Apply"))
        self.assertLess(
            lifecycle.index("docs(openspec): checkpoint <change-name>"),
            lifecycle.index("Recommend Git commits only after native Archive completes successfully"),
        )
        for phrase in (
            "During normal Explore, Propose, Apply, Update, Verify, UAT, and pre-Archive work, do not recommend a Git commit.",
            "routine pre-Archive safety commit",
            "does not mark unfinished tasks complete",
            "If Archive is running or fails, the guidance does not recommend an Archive commit.",
            "strongly recommend the relevant Git commits before the session ends",
            "Git commit guidance is advisory and user controlled",
        ):
            self.assertIn(phrase, lifecycle)

    def test_readme_documents_git_commit_safety_and_no_automatic_mutation(self) -> None:
        root = Path(__file__).parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")
        lifecycle = " ".join(readme[readme.index("## Git lifecycle guidance") :].split())

        self.assertGreaterEqual(lifecycle.count("git commit --only"), 2)
        for phrase in (
            "separate commits for the archived OpenSpec content and the intended",
            "explicit file lists for both commits",
            "no unrelated worktree paths",
            "openspec/changes/archive/<date>-<change-name>/proposal.md",
            "src/custom_openspec_workflow/data/openspec-policy.yaml",
            "`type(scope): subject`",
            "Describe the outcome, not the process",
            "`pre-commit` and `commit-msg` hooks normally",
            "does not recommend `--no-verify` by default",
            "`git revert --no-commit`",
            "recommend a squash merge without requiring it",
            "suggest `git init`",
            "Do not run `git init` automatically",
            "Do not create or modify `.git`",
            "It performs no automatic Git mutation",
        ):
            self.assertIn(phrase, lifecycle)
        for branch in ("main", "master", "trunk", "staging", "develop", "development", "dev"):
            self.assertIn(f"`{branch}`", lifecycle)
        self.assertIn("common protected-branch candidates", lifecycle)
        self.assertIn("Do not claim that a branch is protected or block the commit", lifecycle)

    def test_unsupported_host_is_not_guessed(self) -> None:
        with self.assertRaises(UnsupportedHostError):
            discover_host("claude")

    def test_automated_coverage_uses_a_non_applicable_uat_record(self) -> None:
        root = Path(__file__).parents[1]
        records = (root / "tests" / "fixtures" / "uat-records.md").read_text(encoding="utf-8")
        policy = (root / "src" / "custom_openspec_workflow" / "data" / "openspec-policy.yaml").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        record = next(
            line for line in records.splitlines() if line.startswith("HUMAN UAT - NOT APPLICABLE:")
        )

        self.assertIn("HUMAN UAT - NOT APPLICABLE: <reason>", policy)
        self.assertIn("HUMAN UAT - NOT APPLICABLE:", readme)
        self.assertFalse(record.startswith("- ["))
        self.assertNotIn("PASSED", record)
        self.assertNotIn("WAIVED BY USER", record)

    def test_readme_documents_advisory_install_prerequisites(self) -> None:
        root = Path(__file__).parents[1]
        readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertIn("## Install prerequisites", readme)
        self.assertIn("grill-me/SKILL.md", readme)
        self.assertIn("satya-janghu/agent-skills", readme)
        self.assertIn("simple-english/SKILL.md", readme)
        self.assertIn("AminBlg/SimpleEnglish", readme)
        self.assertIn("npx skills add AminBlg/SimpleEnglish", readme)
        self.assertIn(
            "Grill Me surfaces unclear intent, hidden constraints, decisions, tradeoffs,",
            readme,
        )
        self.assertIn(
            "Simple English helps write clear documentation with short sentences, active",
            readme,
        )
        self.assertIn("does not install, update, or remove Simple English", readme)
        self.assertIn("custom-openspec-init . --openspec-executable /path/to/openspec", readme)
        self.assertIn("`prerequisites`", readme)
        self.assertIn("does not run prerequisite checks during uninstall", readme)

    def test_compatibility_baseline_records_simple_english_metadata_and_contract(self) -> None:
        root = Path(__file__).parents[1]
        baseline = (root / "docs" / "compatibility-baseline.md").read_text(encoding="utf-8")
        fixture = (root / "tests" / "fixtures" / "upstream-skills" / "simple-english" / "SKILL.md").read_text(encoding="utf-8")
        metadata = yaml.safe_load(fixture.split("---", 2)[1])

        self.assertEqual(metadata["name"], "simple-english")
        self.assertEqual(metadata["metadata"]["version"], "2.1.0")
        self.assertIn("AminBlg/SimpleEnglish", baseline)
        self.assertIn("skills/simple-english/SKILL.md", baseline)
        self.assertIn("79b590fc8596523d92c26b1ea7e33236606ef069", baseline)
        self.assertIn(
            f"- Observed skill version: `{metadata['metadata']['version']}`",
            baseline,
        )
        self.assertIn("It reads `<skills-dir>/simple-english/SKILL.md` first.", baseline)
        self.assertIn("when the declared name does not match", baseline)
