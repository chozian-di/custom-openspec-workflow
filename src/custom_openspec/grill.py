"""Stage and attach supplemental context from the upstream Grill Me skill."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import tempfile

from .host import UnsupportedHostError, discover_host
from .paths import grill_skill_path
from .yaml_config import write_text_atomic


REQUIRED_SECTIONS = (
    "Intent",
    "Constraints",
    "Decisions",
    "Assumptions Surfaced",
    "Open Questions",
    "Non-Goals or Out of Scope",
)


class GrillError(RuntimeError):
    """A Grill staging or attachment operation cannot continue safely."""


class ExistingGrillContextError(GrillError):
    """A change already has context and needs an explicit user choice."""


def _skill_name(path: Path, content: str | None = None) -> str:
    text = content if content is not None else path.read_text(encoding="utf-8")
    name = re.search(r"^name:\s*([^\s#]+)", text, re.MULTILINE)
    return name.group(1).strip("'\"") if name else path.parent.name


def discover_grill_me_skill(skills_dir: Path | None = None) -> Path | None:
    """Find the installed upstream Grill Me skill for the supported host."""

    if skills_dir is not None:
        roots = [skills_dir.expanduser().resolve()]
    else:
        try:
            roots = [discover_host("codex").skills_dir]
        except UnsupportedHostError:
            return None

    candidates: list[Path] = []
    for root in roots:
        direct = root / "grill-me" / "SKILL.md"
        if direct.is_file():
            candidates.append(direct)
        if root.is_dir():
            candidates.extend(
                path
                for path in root.rglob("SKILL.md")
                if path.parent.name == "grill-me"
            )

    seen: set[Path] = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        if candidate in seen or not candidate.is_file():
            continue
        seen.add(candidate)
        try:
            content = candidate.read_text(encoding="utf-8")
        except OSError:
            continue
        if _skill_name(candidate, content) == "grill-me":
            return candidate
    return None


@dataclass(frozen=True)
class GrillSession:
    session_id: str
    source_path: Path
    staged_source: Path
    source_sha256: str
    captured_at: str
    staging_dir: Path


def default_staging_dir() -> Path:
    configured = Path.home() / ".local" / "share" / "custom-openspec" / "grill"
    return Path(__import__("os").environ.get("CUSTOM_OPENSPEC_GRILL_HOME", configured)).expanduser()


def _session_id(source_sha256: str, source_path: Path) -> str:
    identity = f"{source_sha256}:{source_path.resolve()}".encode("utf-8")
    return f"grill-{hashlib.sha256(identity).hexdigest()[:20]}"


def _metadata_path(session_dir: Path) -> Path:
    return session_dir / "session.json"


def _load_session(session_dir: Path) -> GrillSession:
    metadata_path = _metadata_path(session_dir)
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GrillError(f"Cannot read Grill session metadata: {metadata_path}") from exc
    required = {"session_id", "source_path", "staged_source", "source_sha256", "captured_at"}
    if not required.issubset(metadata):
        raise GrillError(f"Grill session metadata is incomplete: {metadata_path}")
    return GrillSession(
        session_id=str(metadata["session_id"]),
        source_path=Path(str(metadata["source_path"])),
        staged_source=Path(str(metadata["staged_source"])),
        source_sha256=str(metadata["source_sha256"]),
        captured_at=str(metadata["captured_at"]),
        staging_dir=session_dir.parent,
    )


def stage_source(source: Path, staging_dir: Path | None = None) -> GrillSession:
    source = source.expanduser().resolve()
    if not source.is_file():
        raise GrillError(f"Grill source does not exist: {source}")
    content = source.read_bytes()
    digest = hashlib.sha256(content).hexdigest()
    staging_root = (staging_dir or default_staging_dir()).expanduser().resolve()
    session_id = _session_id(digest, source)
    session_dir = staging_root / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)
    staged_source = session_dir / "source.md"
    staged_source.write_bytes(content)
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    metadata = {
        "session_id": session_id,
        "source_path": str(source),
        "staged_source": str(staged_source),
        "source_sha256": digest,
        "captured_at": captured_at,
        "upstream_skill": "grill-me",
    }
    write_text_atomic(
        _metadata_path(session_dir),
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
    )
    return GrillSession(session_id, source, staged_source, digest, captured_at, staging_root / "sessions")


def find_session(session_id: str, staging_dir: Path | None = None) -> GrillSession:
    if not re.fullmatch(r"grill-[a-f0-9]{20}", session_id):
        raise GrillError("The Grill session identity is invalid")
    root = (staging_dir or default_staging_dir()).expanduser().resolve() / "sessions" / session_id
    if not root.is_dir():
        raise GrillError(f"Grill session was not found: {session_id}")
    session = _load_session(root)
    if not session.staged_source.is_file():
        raise GrillError(f"Staged Grill source is missing: {session.staged_source}")
    return session


def _section_key(title: str) -> str | None:
    normalized = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    if normalized == "intent" or "intent" in normalized:
        return "Intent"
    if "constraint" in normalized:
        return "Constraints"
    if "decision" in normalized:
        return "Decisions"
    if "assumption" in normalized:
        return "Assumptions Surfaced"
    if "open question" in normalized or normalized == "questions":
        return "Open Questions"
    if "non goal" in normalized or "out of scope" in normalized or "scope" == normalized:
        return "Non-Goals or Out of Scope"
    return None


def extract_sections(source: str) -> dict[str, str]:
    """Extract required meaning from headings without relying on exact prose."""

    sections: dict[str, list[str]] = {name: [] for name in REQUIRED_SECTIONS}
    current: str | None = None
    found_heading = False
    for line in source.splitlines():
        heading = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            current = _section_key(heading.group(1))
            found_heading = True
            continue
        if current:
            sections[current].append(line)

    if not found_heading:
        sections["Intent"] = [source.strip()]
    return {name: "\n".join(lines).strip() for name, lines in sections.items()}


def _section_text(value: str) -> str:
    return value if value else "No entries recorded by the upstream Grill Me session."


def render_grill_context(session: GrillSession, source: str) -> str:
    sections = extract_sections(source)
    lines = [
        "# Grill context",
        "",
        f"Source session: `{session.session_id}`",
        f"Source path: `{session.source_path}`",
        f"Source SHA-256: `{session.source_sha256}`",
        f"Captured at: `{session.captured_at}`",
        "Upstream skill: `grill-me`",
        "",
    ]
    for name in REQUIRED_SECTIONS:
        lines.extend([f"## {name}", "", _section_text(sections[name]), ""])
    lines.extend(
        [
            "Resolved decisions stay in Decisions. Unresolved items stay in Open Questions.",
            "This file is supplemental planning context. It is not an OpenSpec schema artifact.",
            "",
        ]
    )
    return "\n".join(lines)


def _existing_session_id(path: Path) -> str | None:
    if not path.is_file():
        return None
    match = re.search(r"^Source session:\s*`?([^`\s]+)`?\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


def _combine_context(existing: str, imported: str, session_id: str) -> str:
    return (
        existing.rstrip()
        + "\n\n---\n\n"
        + f"## Imported Grill session `{session_id}`\n\n"
        + imported.strip()
        + "\n"
    )


def attach_session(
    root: Path,
    change: str,
    session_id: str,
    *,
    staging_dir: Path | None = None,
    replace: bool = False,
    combine: bool = False,
) -> tuple[Path, bool]:
    if "/" in change or "\\" in change or change in {"", ".", ".."}:
        raise GrillError("The change name must be a single OpenSpec change directory name")
    root = root.expanduser().resolve()
    change_dir = root / "openspec" / "changes" / change
    if not change_dir.is_dir():
        raise GrillError(f"OpenSpec change does not exist: {change}")
    session = find_session(session_id, staging_dir)
    destination = change_dir / "grill.md"
    if destination.exists() and not (replace or combine):
        existing_id = _existing_session_id(destination)
        if existing_id == session_id:
            return destination, False
        raise ExistingGrillContextError(
            f"{destination} already exists. Ask the user whether to use --replace "
            "or --combine before changing it."
        )

    source = session.staged_source.read_text(encoding="utf-8")
    imported = render_grill_context(session, source)
    if destination.exists() and combine:
        content = _combine_context(destination.read_text(encoding="utf-8"), imported, session_id)
    else:
        content = imported
    write_text_atomic(destination, content)
    return destination, True


def _file_snapshot(root: Path) -> dict[str, bytes]:
    if root.is_file():
        return {root.name: root.read_bytes()}
    if not root.is_dir():
        return {}
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _adapter_contract() -> dict[str, bool]:
    try:
        skill = grill_skill_path().read_text(encoding="utf-8")
    except (OSError, TypeError):
        return {
            "delegationContractFound": False,
            "optionalUseAvailable": False,
            "adapterDeclaresNoImplementation": False,
        }
    return {
        "delegationContractFound": (
            "upstream `grill-me` skill" in skill
            and "Delegate the requirements session" in skill
        ),
        "optionalUseAvailable": (
            "Skip this skill when normal Explore or Propose already has enough information."
            in skill
        ),
        "adapterDeclaresNoImplementation": (
            "does not implement project changes" in skill
            or "does not perform implementation work" in skill
        ),
    }


def _compatibility_failure(
    source: Path,
    reason: str,
    contract: dict[str, bool],
) -> dict[str, object]:
    return {
        "passed": False,
        "dependencyAvailable": False,
        "dependencyName": "",
        "dependencyPath": "",
        "dependencyError": reason,
        "delegatedSkill": "",
        **contract,
        "sessionId": "",
        "traceable": False,
        "stagedOutsideSourceDirectory": False,
        "stageSucceeded": False,
        "attachmentSucceeded": False,
        "repeatedAttachmentIdempotent": False,
        "requiredSectionsFound": False,
        "missingSections": ", ".join(REQUIRED_SECTIONS),
        "sourceUnchanged": source.is_file(),
        "upstreamUnchanged": None,
        "implementationWork": None,
        "noImplementationWork": False,
        "implementationEvidence": "No implementation evidence was collected because the dependency was unavailable.",
        "failureReason": reason,
    }


def compatibility_check(
    source: Path,
    staging_dir: Path | None = None,
    *,
    skills_dir: Path | None = None,
) -> dict[str, object]:
    """Check the installed Grill Me contract in disposable state."""

    del staging_dir
    source = source.expanduser().resolve()
    dependency = discover_grill_me_skill(skills_dir)
    contract = _adapter_contract()
    if dependency is None:
        hint = str(skills_dir.expanduser().resolve()) if skills_dir else "the Codex user-level skills directory"
        return _compatibility_failure(
            source,
            f"Installed upstream grill-me skill was not found in {hint}. "
            "Install satya-janghu/agent-skills or pass --skills-dir.",
            contract,
        )

    source_before = _file_snapshot(source.parent)
    dependency_before = dependency.read_bytes()
    dependency_digest = _sha256(dependency)
    dependency_name = _skill_name(dependency)
    stage_succeeded = False
    attachment_succeeded = False
    repeated_attachment_idempotent = False
    session_id = ""
    staged_outside_source = False
    traceable = False
    required_sections_found = False
    missing: list[str] = list(REQUIRED_SECTIONS)
    attachment_text = ""
    unexpected_paths: list[str] = []

    with tempfile.TemporaryDirectory(prefix="custom-openspec-grill-") as directory:
        sandbox = Path(directory)
        isolated_staging = sandbox / "staging"
        change_root = sandbox / "openspec" / "changes" / "compatibility-check"
        change_root.mkdir(parents=True)
        try:
            session = stage_source(source, isolated_staging)
            stage_succeeded = session.staged_source.is_file()
            staged_outside_source = session.staged_source.parent != source.parent
            session_id = session.session_id

            destination, first_changed = attach_session(
                sandbox,
                "compatibility-check",
                session.session_id,
                staging_dir=isolated_staging,
            )
            attachment_text = destination.read_text(encoding="utf-8")
            before_repeat = destination.read_bytes()
            _, second_changed = attach_session(
                sandbox,
                "compatibility-check",
                session.session_id,
                staging_dir=isolated_staging,
            )
            repeated_attachment_idempotent = (
                first_changed
                and not second_changed
                and destination.read_bytes() == before_repeat
            )
            attachment_succeeded = destination.is_file() and first_changed

            rendered_sections = extract_sections(attachment_text)
            missing = [
                name for name in REQUIRED_SECTIONS if not rendered_sections[name]
            ]
            required_sections_found = not missing
            traceable = (
                session.session_id in attachment_text
                and str(source) in attachment_text
                and session.source_sha256 in attachment_text
                and _sha256(session.staged_source) == session.source_sha256
            )

            expected_paths = {
                session.staged_source.resolve(),
                (session.staged_source.parent / "session.json").resolve(),
                destination.resolve(),
            }
            unexpected_paths = sorted(
                str(path.relative_to(sandbox))
                for path in sandbox.rglob("*")
                if path.is_file() and path.resolve() not in expected_paths
            )
        except (GrillError, OSError) as exc:
            unexpected_paths = [f"compatibility error: {exc}"]

    source_unchanged = _file_snapshot(source.parent) == source_before
    upstream_unchanged = dependency.read_bytes() == dependency_before
    implementation_work = bool(unexpected_paths) or not source_unchanged or not upstream_unchanged
    no_implementation_work = (
        not implementation_work and contract["adapterDeclaresNoImplementation"]
    )
    failures: list[str] = []
    if not contract["delegationContractFound"]:
        failures.append("the custom skill does not show upstream Grill Me delegation")
    if not contract["optionalUseAvailable"]:
        failures.append("the custom skill does not document optional use")
    if not contract["adapterDeclaresNoImplementation"]:
        failures.append("the custom skill does not declare that it performs no implementation work")
    if not stage_succeeded:
        failures.append("isolated staging did not complete")
    if not attachment_succeeded:
        failures.append("isolated attachment did not complete")
    if not repeated_attachment_idempotent:
        failures.append("repeated attachment was not idempotent")
    if not required_sections_found:
        failures.append(f"required sections are missing: {', '.join(missing)}")
    if not traceable:
        failures.append("attachment does not preserve source traceability")
    if not source_unchanged:
        failures.append("the source directory changed during the compatibility check")
    if not upstream_unchanged:
        failures.append("the installed upstream skill changed during the compatibility check")
    if not no_implementation_work:
        failures.append("implementation-work evidence was not clean")

    return {
        "passed": not failures,
        "dependencyAvailable": True,
        "dependencyName": dependency_name,
        "dependencyPath": str(dependency),
        "dependencySha256": dependency_digest,
        "dependencyError": "",
        "delegatedSkill": dependency_name,
        **contract,
        "sessionId": session_id,
        "traceable": traceable,
        "stagedOutsideSourceDirectory": staged_outside_source,
        "stageSucceeded": stage_succeeded,
        "attachmentSucceeded": attachment_succeeded,
        "repeatedAttachmentIdempotent": repeated_attachment_idempotent,
        "requiredSectionsFound": required_sections_found,
        "missingSections": ", ".join(missing),
        "sourceUnchanged": source_unchanged,
        "upstreamUnchanged": upstream_unchanged,
        "implementationWork": implementation_work,
        "noImplementationWork": no_implementation_work,
        "unexpectedPaths": unexpected_paths,
        "implementationEvidence": (
            "Only the expected isolated staging files and change-local grill.md were written."
            if not implementation_work
            else "Unexpected writes or source changes were detected."
        ),
        "failureReason": "; ".join(failures),
    }
