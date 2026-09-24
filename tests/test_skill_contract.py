from __future__ import annotations

from pathlib import Path
import unittest

from custom_openspec.host import UnsupportedHostError, discover_host


class SkillContractTests(unittest.TestCase):
    def test_adapter_delegates_without_copying_question_logic(self) -> None:
        path = Path(__file__).parents[1] / "src" / "custom_openspec" / "data" / "custom-openspec-grill" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("name: custom-openspec-grill", text)
        self.assertIn("upstream `grill-me` skill", text)
        self.assertNotIn("Question lenses", text)
        self.assertNotIn("Core loop", text)
        self.assertNotIn("one question at a time", text)
        self.assertNotIn("relentlessly", text)

    def test_unsupported_host_is_not_guessed(self) -> None:
        with self.assertRaises(UnsupportedHostError):
            discover_host("claude")

    def test_automated_coverage_uses_a_non_applicable_uat_record(self) -> None:
        root = Path(__file__).parents[1]
        records = (root / "tests" / "fixtures" / "uat-records.md").read_text(encoding="utf-8")
        policy = (root / "src" / "custom_openspec" / "data" / "openspec-policy.yaml").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        record = next(
            line for line in records.splitlines() if line.startswith("HUMAN UAT - NOT APPLICABLE:")
        )

        self.assertIn("HUMAN UAT - NOT APPLICABLE: <reason>", policy)
        self.assertIn("HUMAN UAT - NOT APPLICABLE:", readme)
        self.assertFalse(record.startswith("- ["))
        self.assertNotIn("PASSED", record)
        self.assertNotIn("WAIVED BY USER", record)
