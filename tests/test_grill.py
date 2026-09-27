from __future__ import annotations

import os
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from custom_openspec_workflow.grill import (
    ExistingGrillContextError,
    REQUIRED_SECTIONS,
    attach_session,
    compatibility_check,
    extract_sections,
    render_grill_context,
    stage_source,
)


SOURCE = """# Grill: package policy

## Intent

Create a reusable policy.

## Constraints

Keep stock OpenSpec.

## Key decisions

- Use supported configuration.

## Surfaced assumptions

- Codex reads user skills.

## Open questions

- Which host will be added next?

## Out of scope

- No custom schema.
"""


class GrillTests(unittest.TestCase):
    def test_semantic_heading_extraction_keeps_unresolved_questions_separate(self) -> None:
        sections = extract_sections(SOURCE)
        self.assertEqual(sections["Intent"], "Create a reusable policy.")
        self.assertIn("Use supported configuration.", sections["Decisions"])
        self.assertIn("Which host", sections["Open Questions"])
        self.assertNotIn("Which host", sections["Decisions"])

    def test_stage_and_attach_are_traceable_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".grill" / "generated-slug.md"
            source.parent.mkdir()
            source.write_text(SOURCE, encoding="utf-8")
            staging = root / "user-state"
            session = stage_source(source, staging)
            self.assertTrue(session.staged_source.is_file())
            self.assertNotEqual(session.staged_source.parent, source.parent)
            repeated_session = stage_source(source, staging)
            self.assertEqual(repeated_session.session_id, session.session_id)
            self.assertEqual(repeated_session.source_path, session.source_path)

            change = root / "openspec" / "changes" / "add-policy"
            change.mkdir(parents=True)
            destination, changed = attach_session(root, "add-policy", session.session_id, staging_dir=staging)
            self.assertTrue(changed)
            text = destination.read_text(encoding="utf-8")
            for section in REQUIRED_SECTIONS:
                self.assertIn(f"## {section}", text)
            self.assertIn(session.session_id, text)
            self.assertIn("Open Questions", text)

            same_destination, changed_again = attach_session(
                root, "add-policy", session.session_id, staging_dir=staging
            )
            self.assertEqual(same_destination, destination)
            self.assertFalse(changed_again)

            other_source = root / ".grill" / "other.md"
            other_source.write_text(SOURCE.replace("reusable", "different"), encoding="utf-8")
            other = stage_source(other_source, staging)
            with self.assertRaises(ExistingGrillContextError):
                attach_session(root, "add-policy", other.session_id, staging_dir=staging)

    def test_rendered_context_declares_supplemental_status(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text(SOURCE, encoding="utf-8")
            session = stage_source(source, root / "staging")
            rendered = render_grill_context(session, SOURCE)
            self.assertIn("supplemental planning context", rendered)
            self.assertIn("Resolved decisions stay in Decisions", rendered)

    def test_explicit_staging_directory_overrides_environment_default(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.md"
            source.write_text(SOURCE, encoding="utf-8")
            environment_staging = root / "environment-staging"
            explicit_staging = root / "explicit-staging"

            with patch.dict(
                os.environ,
                {"CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME": str(environment_staging)},
            ):
                session = stage_source(source, explicit_staging)

            self.assertEqual(session.staging_dir, explicit_staging / "sessions")
            self.assertTrue(session.staged_source.is_file())
            self.assertFalse(environment_staging.exists())

    def test_compatibility_discovers_dependency_and_checks_isolated_contract(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".grill" / "generated-slug.md"
            source.parent.mkdir()
            source.write_text(SOURCE, encoding="utf-8")
            skills_dir = root / "skills"
            upstream = skills_dir / "grill-me" / "SKILL.md"
            upstream.parent.mkdir(parents=True)
            upstream.write_text(
                "---\nname: grill-me\n---\nUpstream Grill Me skill.\n",
                encoding="utf-8",
            )
            source_before = source.read_bytes()
            upstream_before = upstream.read_bytes()

            result = compatibility_check(
                source,
                root / "ignored-staging-dir",
                skills_dir=skills_dir,
            )

            self.assertTrue(result["passed"])
            self.assertTrue(result["dependencyAvailable"])
            self.assertEqual(result["dependencyPath"], str(upstream.resolve()))
            self.assertTrue(result["stageSucceeded"])
            self.assertTrue(result["attachmentSucceeded"])
            self.assertTrue(result["repeatedAttachmentIdempotent"])
            self.assertTrue(result["requiredSectionsFound"])
            self.assertTrue(result["traceable"])
            self.assertTrue(result["sourceUnchanged"])
            self.assertTrue(result["upstreamUnchanged"])
            self.assertFalse(result["implementationWork"])
            self.assertTrue(result["noImplementationWork"])
            self.assertFalse((root / "ignored-staging-dir").exists())
            self.assertEqual(source.read_bytes(), source_before)
            self.assertEqual(upstream.read_bytes(), upstream_before)

    def test_compatibility_reports_missing_dependency_without_writing_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".grill" / "source.md"
            source.parent.mkdir()
            source.write_text(SOURCE, encoding="utf-8")
            before = source.read_bytes()

            result = compatibility_check(source, skills_dir=root / "missing-skills")

            self.assertFalse(result["passed"])
            self.assertFalse(result["dependencyAvailable"])
            self.assertIn(str((root / "missing-skills").resolve()), result["failureReason"])
            self.assertIn("Install satya-janghu/agent-skills", result["failureReason"])
            self.assertIn("skills/grill-me", result["failureReason"])
            self.assertIn("package README", result["failureReason"])
            self.assertEqual(source.read_bytes(), before)
