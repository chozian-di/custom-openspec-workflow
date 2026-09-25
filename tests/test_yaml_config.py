from __future__ import annotations

import unittest

from custom_openspec_workflow.yaml_config import ConfigurationError, merge_policy


POLICY = {
    "rules": {
        "proposal": ["Read Grill context."],
        "tasks": ["Use stock tasks.md."],
    },
    "operations": {
        "apply": {"guidance": ["Apply guidance is advisory."]},
        "archive": {"guidance": ["Run Verify first."]},
    },
}


class MergePolicyTests(unittest.TestCase):
    def test_merge_preserves_project_values_and_is_idempotent(self) -> None:
        original = {
            "schema": "spec-driven",
            "context": "Keep this project context.",
            "rules": {"proposal": ["Project rule."]},
            "operations": {"apply": {"guidance": ["Project guidance."]}},
            "projectField": {"owner": "user"},
        }
        first = merge_policy(original, POLICY)
        self.assertEqual(first.configuration["context"], original["context"])
        self.assertEqual(first.configuration["projectField"], original["projectField"])
        self.assertIn("Read Grill context.", first.configuration["rules"]["proposal"])
        self.assertEqual(len(first.configuration["rules"]["proposal"]), 2)

        second = merge_policy(first.configuration, POLICY)
        self.assertEqual(second.configuration, first.configuration)
        self.assertEqual(second.changes, [])

    def test_malformed_project_policy_field_is_rejected(self) -> None:
        with self.assertRaises(ConfigurationError):
            merge_policy({"schema": "spec-driven", "rules": "not-a-map"}, POLICY)

    def test_existing_exact_duplicate_is_reported_without_data_loss(self) -> None:
        result = merge_policy(
            {"schema": "spec-driven", "rules": {"proposal": ["Read Grill context."] * 2}},
            POLICY,
        )
        self.assertEqual(result.configuration["rules"]["proposal"].count("Read Grill context."), 2)
        self.assertTrue(result.warnings)
