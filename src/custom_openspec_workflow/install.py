"""Install and uninstall the custom helper and skill safely.

The command operates on user-level files only. It builds a complete plan
before it writes, records ownership in a manifest, and uses content hashes to
avoid replacing or removing files that a user changed.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import sys
import tempfile
from typing import Any, Iterable, Sequence

from . import PROJECT_IDENTITY
from .grill import (
    GRILL_ME_VALUE,
    SIMPLE_ENGLISH_VALUE,
    discover_grill_me_skill,
    discover_simple_english_skill,
    grill_me_install_hint,
    simple_english_install_hint,
)
from .host import HostLayout, UnsupportedHostError, discover_host, executable_in_path
from .paths import default_cache_root, default_data_root


MANIFEST_FILENAME = "manifest.json"
MANIFEST_VERSION = 1
MANIFEST_FORMAT = "custom-openspec-workflow-install"

WRAPPER_MODULES = {
    "custom-openspec-init": "custom_openspec_workflow.bootstrap",
    "custom-openspec-grill": "custom_openspec_workflow.grill_cli",
}


class InstallError(RuntimeError):
    """The installation operation cannot continue safely."""


class InstallConflictError(InstallError):
    """The operation found an unmanaged or user-modified path."""

    def __init__(self, message: str, plan: "OperationPlan | None" = None) -> None:
        super().__init__(message)
        self.plan = plan


class InstallApplyError(InstallError):
    """The operation failed while applying a previously validated plan."""


@dataclass(frozen=True)
class PlanEntry:
    """One file or directory operation in an install plan."""

    operation: str
    path: Path
    kind: str
    reason: str | None = None
    sha256: str | None = None
    mode: int | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "operation": self.operation,
            "path": str(self.path),
            "kind": self.kind,
        }
        if self.reason is not None:
            result["reason"] = self.reason
        if self.sha256 is not None:
            result["sha256"] = self.sha256
        if self.mode is not None:
            result["mode"] = self.mode
        return result


@dataclass(frozen=True)
class ExpectedFile:
    """Content that an install operation expects at one target path."""

    path: Path
    kind: str
    data: bytes
    mode: int

    @property
    def sha256(self) -> str:
        return _sha256_bytes(self.data)


@dataclass(frozen=True)
class PrerequisiteResult:
    """One read-only result for a feature prerequisite."""

    name: str
    feature: str
    kind: str
    status: str
    checked: str
    resolved: str | None = None
    remediation: str = ""
    value: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "feature": self.feature,
            "kind": self.kind,
            "status": self.status,
            "checked": self.checked,
            "resolved": self.resolved,
            "remediation": self.remediation,
            "value": self.value,
        }


@dataclass
class OperationPlan:
    """A read-only description of an install or uninstall operation."""

    operation: str
    host: str
    skills_dir: Path
    bin_dir: Path
    install_root: Path
    manifest_path: Path
    entries: list[PlanEntry] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    modified: list[str] = field(default_factory=list)
    expected_files: dict[Path, ExpectedFile] = field(default_factory=dict)
    previous_files: dict[Path, dict[str, Any]] = field(default_factory=dict)
    previous_directories: set[Path] = field(default_factory=set)
    final_directories: set[Path] = field(default_factory=set)
    manifest_data: dict[str, Any] | None = None
    manifest_trusted: bool = False
    prerequisites: list[PrerequisiteResult] = field(default_factory=list)

    @property
    def is_blocked(self) -> bool:
        return bool(self.conflicts)

    def to_dict(self, *, dry_run: bool = False) -> dict[str, Any]:
        package_path = self.install_root / "custom_openspec_workflow"
        skill_path = self.skills_dir / "custom-openspec-grill" / "SKILL.md"
        wrappers = [self.bin_dir / name for name in WRAPPER_MODULES]
        return {
            "operation": self.operation,
            "host": self.host,
            "skillsDir": str(self.skills_dir),
            "binDir": str(self.bin_dir),
            "installDir": str(self.install_root),
            "package": str(package_path),
            "skill": str(skill_path),
            "wrappers": [str(path) for path in wrappers],
            "manifest": str(self.manifest_path),
            "manifestPath": str(self.manifest_path),
            "plan": [entry.to_dict() for entry in self.entries],
            "conflicts": list(self.conflicts),
            "modified": list(self.modified),
            "prerequisites": [item.to_dict() for item in self.prerequisites],
            "dryRun": dry_run,
            "status": "blocked" if self.is_blocked else "planned",
            "applied": False,
        }


def _source_package_root() -> Path:
    return Path(__file__).resolve().parent


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_file(path: Path) -> str:
    """Return the SHA-256 content hash for a regular file."""

    if path.is_symlink() or not path.is_file():
        raise InstallError(f"Cannot hash a non-regular file: {path}")
    return _sha256_bytes(path.read_bytes())


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


def _lexists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _path_kind(path: Path) -> str:
    if not _lexists(path):
        return "missing"
    if path.is_symlink():
        return "symlink"
    if path.is_dir():
        return "directory"
    if path.is_file():
        return "file"
    return "other"


def _path_is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _wrapper_content(install_root: Path, module: str) -> bytes:
    content = (
        "#!/bin/sh\n"
        "set -eu\n"
        'if [ "${PYTHONPYCACHEPREFIX+x}" != x ]; then\n'
        f"    PYTHONPYCACHEPREFIX={shlex.quote(str(default_cache_root()))}\n"
        "fi\n"
        "export PYTHONPYCACHEPREFIX\n"
        f"exec python3 - {shlex.quote(str(install_root))} \"$@\" <<'PY'\n"
        "import sys\n"
        "install_root = sys.argv.pop(1)\n"
        "sys.path.insert(0, install_root)\n"
        f"from {module} import main\n"
        "raise SystemExit(main())\n"
        "PY\n"
    )
    return content.encode("utf-8")


def _source_files(source_package: Path) -> list[tuple[Path, Path]]:
    """Return source and relative paths, excluding Python bytecode caches."""

    files: list[tuple[Path, Path]] = []
    for source in sorted(source_package.rglob("*")):
        if source.is_dir():
            continue
        relative = source.relative_to(source_package)
        if "__pycache__" in relative.parts or source.suffix == ".pyc":
            continue
        if source.is_symlink() or not source.is_file():
            raise InstallError(f"Package source contains an unsupported path: {source}")
        files.append((source, relative))
    return files


def _resolve_layout(
    host: str | None,
    skills_dir: Path | None,
    bin_dir: Path | None,
) -> HostLayout:
    selected_host = host or os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_HOST", "codex")
    if selected_host.lower() != "codex":
        raise UnsupportedHostError(
            f"Unsupported host {selected_host!r}. This package supports Codex only."
        )
    if skills_dir is not None and bin_dir is not None:
        return HostLayout(
            "codex",
            skills_dir.expanduser().resolve(),
            bin_dir.expanduser().resolve(),
        )
    discovered = discover_host(selected_host)
    return HostLayout(
        "codex",
        (skills_dir or discovered.skills_dir).expanduser().resolve(),
        (bin_dir or discovered.bin_dir).expanduser().resolve(),
    )


def _resolve_install_root(install_dir: Path | None) -> Path:
    return (install_dir if install_dir is not None else default_data_root()).expanduser().resolve()


def _required_directories(paths: Iterable[Path]) -> set[Path]:
    """Return every parent directory needed for the supplied file paths."""

    result: set[Path] = set()
    for path in paths:
        current = path.parent
        while True:
            result.add(current)
            if _lexists(current):
                break
            parent = current.parent
            if parent == current:
                break
            current = parent
    return result


def _record_for_path(path: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "sha256": metadata["sha256"],
        "mode": int(metadata["mode"]),
        "kind": str(metadata.get("kind", "file")),
    }


def _manifest_without_self_hash(manifest: dict[str, Any]) -> bytes:
    normalized = dict(manifest)
    normalized["manifestSha256"] = ""
    return (json.dumps(normalized, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _finalize_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    result = dict(manifest)
    result["manifestSha256"] = _sha256_bytes(_manifest_without_self_hash(result))
    return result


def serialize_manifest(manifest: dict[str, Any]) -> bytes:
    """Serialize a manifest with its normalized self-hash."""

    finalized = _finalize_manifest(manifest)
    return (json.dumps(finalized, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _read_manifest(
    manifest_path: Path,
    *,
    install_root: Path,
    skills_dir: Path,
    bin_dir: Path,
) -> tuple[dict[str, Any] | None, str | None]:
    """Read and validate the ownership manifest without changing files."""

    if not _lexists(manifest_path):
        return None, None
    if _path_kind(manifest_path) != "file":
        return None, f"Ownership manifest is not a regular file: {manifest_path}"
    try:
        raw = manifest_path.read_bytes()
        manifest = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return None, f"Ownership manifest is unreadable: {manifest_path} ({exc})"
    if not isinstance(manifest, dict):
        return None, "Ownership manifest must contain a JSON object"
    if manifest.get("format") != MANIFEST_FORMAT:
        return None, "Ownership manifest has an unsupported format"
    if manifest.get("version") != MANIFEST_VERSION:
        return None, "Ownership manifest has an unsupported version"
    if manifest.get("manifestSha256") != _sha256_bytes(
        _manifest_without_self_hash(manifest)
    ):
        return None, "Ownership manifest content hash does not match"
    if manifest.get("installRoot") != str(install_root):
        return None, "Ownership manifest install root does not match the selected install root"
    if manifest.get("skillsDir") != str(skills_dir):
        return None, "Ownership manifest skills directory does not match the selected skills directory"
    if manifest.get("binDir") != str(bin_dir):
        return None, "Ownership manifest executable directory does not match the selected executable directory"
    if manifest.get("manifestPath") != str(manifest_path):
        return None, "Ownership manifest path does not match the selected install root"

    files = manifest.get("files")
    if not isinstance(files, dict):
        return None, "Ownership manifest files must be a JSON object"
    package_root = install_root / "custom_openspec_workflow"
    skill_path = skills_dir / "custom-openspec-grill" / "SKILL.md"
    wrapper_paths = {bin_dir / name for name in WRAPPER_MODULES}
    parsed_files: dict[str, dict[str, Any]] = {}
    for raw_path, raw_metadata in files.items():
        if not isinstance(raw_path, str) or not isinstance(raw_metadata, dict):
            return None, "Ownership manifest contains an invalid file record"
        path = Path(raw_path)
        if not path.is_absolute() or path != path.resolve():
            return None, f"Ownership manifest path is not an absolute normalized path: {raw_path}"
        if not (
            _path_is_within(path, package_root)
            or path == skill_path
            or path in wrapper_paths
        ):
            return None, f"Ownership manifest names an out-of-scope path: {path}"
        digest = raw_metadata.get("sha256")
        mode = raw_metadata.get("mode")
        if not isinstance(digest, str) or len(digest) != 64:
            return None, f"Ownership manifest has an invalid hash for: {path}"
        try:
            int(digest, 16)
            mode_value = int(mode)
        except (TypeError, ValueError):
            return None, f"Ownership manifest has invalid metadata for: {path}"
        if mode_value < 0 or mode_value > 0o7777:
            return None, f"Ownership manifest has an invalid mode for: {path}"
        parsed_files[str(path)] = _record_for_path(
            path,
            {
                "sha256": digest,
                "mode": mode_value,
                "kind": raw_metadata.get("kind", "file"),
            },
        )
    manifest["files"] = parsed_files

    directories = manifest.get("directories", [])
    if not isinstance(directories, list) or not all(
        isinstance(item, str) for item in directories
    ):
        return None, "Ownership manifest directories must be a list of paths"
    allowed_dir_anchors = (install_root, skills_dir, bin_dir)
    parsed_directories: set[Path] = set()
    for raw_directory in directories:
        path = Path(raw_directory)
        if not path.is_absolute() or path != path.resolve():
            return None, f"Ownership manifest directory is not normalized: {raw_directory}"
        if not any(
            path == anchor or _path_is_within(path, anchor)
            for anchor in allowed_dir_anchors
        ):
            return None, f"Ownership manifest names an out-of-scope directory: {path}"
        parsed_directories.add(path)
    manifest["directories"] = [str(path) for path in sorted(parsed_directories)]
    return manifest, None


def read_manifest(
    manifest_path: Path,
    *,
    install_root: Path,
    skills_dir: Path,
    bin_dir: Path,
) -> dict[str, Any]:
    """Read a trusted ownership manifest or raise ``InstallError``."""

    manifest, error = _read_manifest(
        manifest_path,
        install_root=install_root,
        skills_dir=skills_dir,
        bin_dir=bin_dir,
    )
    if error or manifest is None:
        raise InstallError(error or f"Ownership manifest does not exist: {manifest_path}")
    return manifest


def _expected_files(
    source_package: Path,
    install_root: Path,
    skills_dir: Path,
    bin_dir: Path,
) -> dict[Path, ExpectedFile]:
    if not source_package.is_dir():
        raise UnsupportedHostError(f"Package source does not exist: {source_package}")
    result: dict[Path, ExpectedFile] = {}
    for source, relative in _source_files(source_package):
        target = install_root / "custom_openspec_workflow" / relative
        result[target] = ExpectedFile(
            target,
            "package",
            source.read_bytes(),
            _mode(source),
        )

    skill_source = source_package / "data" / "custom-openspec-grill" / "SKILL.md"
    if not skill_source.is_file() or skill_source.is_symlink():
        raise InstallError(f"Custom Grill skill source does not exist: {skill_source}")
    skill_target = skills_dir / "custom-openspec-grill" / "SKILL.md"
    result[skill_target] = ExpectedFile(
        skill_target,
        "skill",
        skill_source.read_bytes(),
        _mode(skill_source),
    )

    for name, module in WRAPPER_MODULES.items():
        target = bin_dir / name
        result[target] = ExpectedFile(
            target,
            "wrapper",
            _wrapper_content(install_root, module),
            0o755,
        )
    return result


def _collect_prerequisites(layout: HostLayout) -> list[PrerequisiteResult]:
    """Collect install-only prerequisite results without changing user paths."""

    grill_me = discover_grill_me_skill(layout.skills_dir)
    grill_result = PrerequisiteResult(
        name="grill-me",
        feature="custom-openspec-grill",
        kind="skill",
        status="available" if grill_me is not None else "missing",
        checked=str(layout.skills_dir),
        resolved=str(grill_me) if grill_me is not None else None,
        remediation="" if grill_me is not None else grill_me_install_hint(),
        value=GRILL_ME_VALUE,
    )
    simple_english = discover_simple_english_skill(layout.skills_dir)
    simple_english_result = PrerequisiteResult(
        name="simple-english",
        feature="documentation-writing",
        kind="skill",
        status="available" if simple_english is not None else "missing",
        checked=str(layout.skills_dir),
        resolved=str(simple_english) if simple_english is not None else None,
        remediation=(
            "" if simple_english is not None else simple_english_install_hint()
        ),
        value=SIMPLE_ENGLISH_VALUE,
    )

    openspec = executable_in_path("openspec")
    openspec_result = PrerequisiteResult(
        name="openspec",
        feature="custom-openspec-init",
        kind="executable",
        status="available" if openspec is not None else "missing",
        checked="openspec on PATH",
        resolved=str(openspec) if openspec is not None else None,
        remediation=(
            "Install OpenSpec so the default `openspec` command is on PATH, or "
            "pass an explicit `--openspec-executable` value to `custom-openspec-init`."
            if openspec is None
            else ""
        ),
    )
    return [grill_result, simple_english_result, openspec_result]


def _add_conflict(plan: OperationPlan, path: Path, reason: str, *, kind: str = "file") -> None:
    message = f"{path}: {reason}"
    if message not in plan.conflicts:
        plan.conflicts.append(message)
    if not any(entry.path == path and entry.operation == "conflict" for entry in plan.entries):
        plan.entries.append(PlanEntry("conflict", path, kind, reason=reason))


def _file_matches_record(path: Path, record: dict[str, Any]) -> bool:
    return _path_kind(path) == "file" and hash_file(path) == record["sha256"]


def _file_matches_expected(path: Path, expected: ExpectedFile) -> bool:
    return _path_kind(path) == "file" and hash_file(path) == expected.sha256


def _iter_existing_entries(root: Path) -> Iterable[Path]:
    if _path_kind(root) != "directory":
        return []
    return sorted(root.rglob("*"))


def _directory_entries(plan: OperationPlan, required_dirs: set[Path]) -> None:
    for directory in sorted(required_dirs, key=lambda item: (len(item.parts), str(item))):
        kind = _path_kind(directory)
        if kind == "missing":
            plan.entries.append(PlanEntry("create", directory, "directory"))
        elif kind == "directory":
            plan.entries.append(PlanEntry("preserve", directory, "directory"))
        else:
            _add_conflict(
                plan,
                directory,
                "required directory is not a real directory",
                kind="directory",
            )


def _manifest_directory_allowed(
    directory: Path,
    *,
    install_root: Path,
    skills_dir: Path,
    bin_dir: Path,
) -> bool:
    return any(
        directory == anchor or _path_is_within(directory, anchor)
        for anchor in (install_root, skills_dir, bin_dir)
    )


def build_install_plan(
    *,
    host: str | None = None,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
    install_dir: Path | None = None,
    source_root: Path | None = None,
) -> OperationPlan:
    """Build an install plan without changing any user-level path."""

    layout = _resolve_layout(host, skills_dir, bin_dir)
    source_package = (source_root or _source_package_root()).expanduser().resolve()
    destination = _resolve_install_root(install_dir)
    manifest_path = destination / MANIFEST_FILENAME
    expected = _expected_files(source_package, destination, layout.skills_dir, layout.bin_dir)
    plan = OperationPlan(
        "install",
        layout.name,
        layout.skills_dir,
        layout.bin_dir,
        destination,
        manifest_path,
        expected_files=expected,
        prerequisites=_collect_prerequisites(layout),
    )

    manifest, manifest_error = _read_manifest(
        manifest_path,
        install_root=destination,
        skills_dir=layout.skills_dir,
        bin_dir=layout.bin_dir,
    )
    if manifest_error:
        _add_conflict(plan, manifest_path, manifest_error, kind="manifest")
    elif manifest is not None:
        plan.manifest_trusted = True
        plan.previous_files = {
            Path(path): dict(metadata) for path, metadata in manifest["files"].items()
        }
        plan.previous_directories = {Path(path) for path in manifest["directories"]}

    required_dirs = _required_directories(expected)
    _directory_entries(plan, required_dirs)

    expected_paths = set(expected)
    previous_paths = set(plan.previous_files)

    for path in sorted(expected_paths):
        item = expected[path]
        kind = _path_kind(path)
        if kind == "missing":
            plan.entries.append(
                PlanEntry("create", path, item.kind, sha256=item.sha256, mode=item.mode)
            )
            continue
        if kind != "file":
            _add_conflict(plan, path, "install target is not a regular file", kind=item.kind)
            continue
        record = plan.previous_files.get(path)
        if record is not None:
            if _file_matches_record(path, record):
                operation = "preserve" if _file_matches_expected(path, item) else "replace"
                plan.entries.append(
                    PlanEntry(operation, path, item.kind, sha256=item.sha256, mode=item.mode)
                )
            else:
                _add_conflict(
                    plan,
                    path,
                    "managed file was modified outside the installer",
                    kind=item.kind,
                )
        else:
            _add_conflict(
                plan,
                path,
                "existing path is not recorded as package-owned",
                kind=item.kind,
            )

    remove_paths: set[Path] = set()
    for path in sorted(previous_paths - expected_paths):
        record = plan.previous_files[path]
        kind = _path_kind(path)
        if kind == "missing":
            continue
        if kind == "file" and _file_matches_record(path, record):
            plan.entries.append(
                PlanEntry(
                    "remove",
                    path,
                    str(record.get("kind", "package")),
                    reason="no longer part of the installed package",
                )
            )
            remove_paths.add(path)
        else:
            _add_conflict(
                plan,
                path,
                "managed file was modified outside the installer",
                kind=str(record.get("kind", "package")),
            )

    scan_roots = {
        destination / "custom_openspec_workflow",
        layout.skills_dir / "custom-openspec-grill",
    }
    for scan_root in sorted(scan_roots, key=str):
        for path in _iter_existing_entries(scan_root):
            if path in expected_paths or path in previous_paths:
                continue
            if path.is_file() or path.is_symlink():
                _add_conflict(plan, path, "existing path is not recorded as package-owned")

    old_dirs_to_remove: set[Path] = set()
    if plan.manifest_trusted:
        for directory in sorted(
            plan.previous_directories,
            key=lambda item: (-len(item.parts), str(item)),
        ):
            if directory == destination or directory in required_dirs:
                continue
            kind = _path_kind(directory)
            if kind == "missing":
                continue
            if kind != "directory":
                _add_conflict(
                    plan,
                    directory,
                    "managed directory is no longer a directory",
                    kind="directory",
                )
                continue
            remaining = [
                child
                for child in directory.iterdir()
                if child not in remove_paths and child not in old_dirs_to_remove
            ]
            if not remaining:
                plan.entries.append(
                    PlanEntry("remove", directory, "directory", reason="empty installer-created directory")
                )
                old_dirs_to_remove.add(directory)
            else:
                plan.entries.append(
                    PlanEntry("preserve", directory, "directory", reason="directory contains unrelated files")
                )

    plan.final_directories = {
        directory
        for directory in plan.previous_directories
        if directory not in old_dirs_to_remove
        and _lexists(directory)
        and _manifest_directory_allowed(
            directory,
            install_root=destination,
            skills_dir=layout.skills_dir,
            bin_dir=layout.bin_dir,
        )
    }
    plan.final_directories.update(
        directory
        for directory in required_dirs
        if _manifest_directory_allowed(
            directory,
            install_root=destination,
            skills_dir=layout.skills_dir,
            bin_dir=layout.bin_dir,
        )
        and any(
            entry.path == directory and entry.operation == "create"
            for entry in plan.entries
        )
    )

    manifest_files = {
        str(path): {
            "sha256": item.sha256,
            "mode": item.mode,
            "kind": item.kind,
        }
        for path, item in sorted(expected.items(), key=lambda pair: str(pair[0]))
    }
    plan.manifest_data = _finalize_manifest(
        {
            "format": MANIFEST_FORMAT,
            "version": MANIFEST_VERSION,
            "installRoot": str(destination),
            "host": layout.name,
            "skillsDir": str(layout.skills_dir),
            "binDir": str(layout.bin_dir),
            "manifestPath": str(manifest_path),
            "files": manifest_files,
            "directories": [str(path) for path in sorted(plan.final_directories)],
        }
    )
    if manifest_error is None:
        manifest_kind = "create" if _path_kind(manifest_path) == "missing" else "replace"
        plan.entries.append(PlanEntry(manifest_kind, manifest_path, "manifest"))
    return plan


def build_uninstall_plan(
    *,
    host: str | None = None,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
    install_dir: Path | None = None,
) -> OperationPlan:
    """Build an uninstall plan from a trusted ownership manifest."""

    layout = _resolve_layout(host, skills_dir, bin_dir)
    destination = _resolve_install_root(install_dir)
    manifest_path = destination / MANIFEST_FILENAME
    plan = OperationPlan(
        "uninstall",
        layout.name,
        layout.skills_dir,
        layout.bin_dir,
        destination,
        manifest_path,
    )
    manifest, manifest_error = _read_manifest(
        manifest_path,
        install_root=destination,
        skills_dir=layout.skills_dir,
        bin_dir=layout.bin_dir,
    )
    if manifest_error:
        _add_conflict(plan, manifest_path, manifest_error, kind="manifest")
        return plan
    if manifest is None:
        _add_conflict(
            plan,
            manifest_path,
            "no trustworthy ownership manifest was found",
            kind="manifest",
        )
        return plan

    plan.manifest_trusted = True
    plan.previous_files = {
        Path(path): dict(metadata) for path, metadata in manifest["files"].items()
    }
    plan.previous_directories = {Path(path) for path in manifest["directories"]}
    remove_paths: set[Path] = set()
    for path, record in sorted(plan.previous_files.items(), key=lambda pair: str(pair[0])):
        kind = _path_kind(path)
        if kind == "missing":
            plan.entries.append(
                PlanEntry(
                    "preserve",
                    path,
                    str(record.get("kind", "file")),
                    reason="already absent",
                )
            )
        elif kind == "file" and _file_matches_record(path, record):
            plan.entries.append(
                PlanEntry(
                    "remove",
                    path,
                    str(record.get("kind", "file")),
                    reason="unchanged package-owned file",
                )
            )
            remove_paths.add(path)
        else:
            reason = "managed file was modified outside the installer"
            plan.entries.append(
                PlanEntry("preserve", path, str(record.get("kind", "file")), reason=reason)
            )
            plan.modified.append(str(path))

    if _path_kind(manifest_path) == "file":
        plan.entries.append(PlanEntry("remove", manifest_path, "manifest", reason="ownership manifest"))
        remove_paths.add(manifest_path)

    for directory in sorted(
        plan.previous_directories,
        key=lambda item: (-len(item.parts), str(item)),
    ):
        if directory == destination:
            continue
        kind = _path_kind(directory)
        if kind == "missing":
            continue
        if kind != "directory":
            plan.entries.append(
                PlanEntry("preserve", directory, "directory", reason="path is not a directory")
            )
            continue
        remaining = [child for child in directory.iterdir() if child not in remove_paths]
        if not remaining:
            plan.entries.append(
                PlanEntry("remove", directory, "directory", reason="empty installer-created directory")
            )
            remove_paths.add(directory)
        else:
            plan.entries.append(
                PlanEntry(
                    "preserve",
                    directory,
                    "directory",
                    reason="directory contains unrelated files",
                )
            )

    plan.final_directories = set(plan.previous_directories)
    return plan


def _atomic_write_bytes(path: Path, data: bytes, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
        )
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, path)
        temporary_name = None
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink()
            except FileNotFoundError:
                pass


def _remove_file(path: Path) -> None:
    if _path_kind(path) in {"file", "symlink"}:
        path.unlink()


def _snapshot_files(paths: Iterable[Path]) -> dict[Path, tuple[bytes, int]]:
    snapshot: dict[Path, tuple[bytes, int]] = {}
    for path in paths:
        if _path_kind(path) == "file":
            snapshot[path] = (path.read_bytes(), _mode(path))
    return snapshot


def _restore_snapshot(
    paths: Iterable[Path],
    snapshot: dict[Path, tuple[bytes, int]],
    *,
    directories: Iterable[Path] = (),
) -> None:
    for directory in sorted(set(directories), key=lambda item: (len(item.parts), str(item))):
        if _path_kind(directory) == "missing":
            directory.mkdir(parents=True, exist_ok=True)
    for path in paths:
        kind = _path_kind(path)
        if kind == "directory":
            raise InstallApplyError(f"Cannot restore file over directory: {path}")
        if kind in {"file", "symlink"}:
            path.unlink()
        if path in snapshot:
            data, mode = snapshot[path]
            _atomic_write_bytes(path, data, mode)


def _cleanup_new_directories(directories: Iterable[Path]) -> None:
    for directory in sorted(set(directories), key=lambda item: (-len(item.parts), str(item))):
        if _path_kind(directory) != "directory":
            continue
        try:
            directory.rmdir()
        except OSError:
            pass


def _stage_expected_files(
    expected: Iterable[ExpectedFile],
    stage_root: Path,
) -> dict[Path, Path]:
    stage_root.mkdir(parents=True, exist_ok=True)
    staged: dict[Path, Path] = {}
    for index, item in enumerate(expected):
        stage_path = stage_root / str(index)
        stage_path.write_bytes(item.data)
        stage_path.chmod(item.mode)
        staged[item.path] = stage_path
    return staged


def _apply_install_plan(plan: OperationPlan) -> list[str]:
    if plan.is_blocked:
        raise InstallConflictError("Install plan contains conflicts", plan)
    if plan.manifest_data is None:
        raise InstallError("Install plan has no manifest data")

    file_entries = [entry for entry in plan.entries if entry.kind != "directory"]
    touched_paths = {
        entry.path
        for entry in file_entries
        if entry.operation in {"create", "replace", "remove"}
    }
    created_directories = {
        entry.path
        for entry in plan.entries
        if entry.kind == "directory" and entry.operation == "create"
    }
    snapshot = _snapshot_files(touched_paths)
    originally_existing = {path for path in touched_paths if _lexists(path)}
    changed: list[str] = []
    removed_directories: list[Path] = []
    try:
        with tempfile.TemporaryDirectory(prefix="custom-openspec-install-") as temporary:
            stage_root = Path(temporary)
            staged = _stage_expected_files(plan.expected_files.values(), stage_root / "files")
            manifest_stage = stage_root / "manifest.json"
            manifest_stage.write_bytes(serialize_manifest(plan.manifest_data))
            manifest_stage.chmod(0o644)

            for directory in sorted(created_directories, key=lambda item: (len(item.parts), str(item))):
                if _path_kind(directory) == "missing":
                    directory.mkdir(parents=False, exist_ok=False)
                elif _path_kind(directory) != "directory":
                    raise InstallApplyError(f"Required directory changed during install: {directory}")

            for path, item in sorted(plan.expected_files.items(), key=lambda pair: str(pair[0])):
                entry = next(
                    (
                        candidate
                        for candidate in plan.entries
                        if candidate.path == path and candidate.kind != "directory"
                    ),
                    None,
                )
                if entry is None or entry.operation not in {"create", "replace"}:
                    continue
                _atomic_write_bytes(path, staged[path].read_bytes(), item.mode)
                changed.append(str(path))

            for entry in plan.entries:
                if entry.operation != "remove" or entry.kind == "directory":
                    continue
                if _path_kind(entry.path) == "file":
                    _remove_file(entry.path)
                    changed.append(str(entry.path))

            _atomic_write_bytes(plan.manifest_path, manifest_stage.read_bytes(), 0o644)
            changed.append(str(plan.manifest_path))

            for entry in sorted(
                (
                    item
                    for item in plan.entries
                    if item.operation == "remove" and item.kind == "directory"
                ),
                key=lambda item: (-len(item.path.parts), str(item.path)),
            ):
                if _path_kind(entry.path) == "directory":
                    entry.path.rmdir()
                    removed_directories.append(entry.path)
                    changed.append(str(entry.path))

            for path, item in plan.expected_files.items():
                if _path_kind(path) != "file" or hash_file(path) != item.sha256:
                    raise InstallApplyError(f"Installed content verification failed: {path}")
    except Exception as exc:
        try:
            _restore_snapshot(touched_paths, snapshot, directories=removed_directories)
            created_before_apply = {
                path for path in created_directories if path in originally_existing
            }
            _cleanup_new_directories(created_directories - created_before_apply)
        except Exception as rollback_error:
            raise InstallApplyError(
                f"Install failed: {exc}; rollback failed: {rollback_error}"
            ) from exc
        if isinstance(exc, InstallError):
            raise
        raise InstallApplyError(f"Install failed and was rolled back: {exc}") from exc
    return changed


def _apply_uninstall_plan(plan: OperationPlan) -> list[str]:
    if plan.is_blocked:
        raise InstallConflictError("Uninstall plan contains conflicts", plan)
    removable_files = [
        entry.path
        for entry in plan.entries
        if entry.operation == "remove" and entry.kind != "directory"
    ]
    removable_directories = [
        entry.path
        for entry in plan.entries
        if entry.operation == "remove" and entry.kind == "directory"
    ]
    snapshot = _snapshot_files(removable_files)
    changed: list[str] = []
    removed_directories: list[Path] = []
    try:
        for path in removable_files:
            if _path_kind(path) == "file":
                _remove_file(path)
                changed.append(str(path))
        for path in sorted(removable_directories, key=lambda item: (-len(item.parts), str(item))):
            if _path_kind(path) == "directory":
                path.rmdir()
                removed_directories.append(path)
                changed.append(str(path))
    except Exception as exc:
        try:
            _restore_snapshot(removable_files, snapshot, directories=removed_directories)
        except Exception as rollback_error:
            raise InstallApplyError(
                f"Uninstall failed: {exc}; rollback failed: {rollback_error}"
            ) from exc
        raise InstallApplyError(f"Uninstall failed and was rolled back: {exc}") from exc
    return changed


def _completed_payload(plan: OperationPlan, *, dry_run: bool = False) -> dict[str, Any]:
    payload = plan.to_dict(dry_run=dry_run)
    payload["status"] = "dry-run" if dry_run else "completed"
    payload["applied"] = False if dry_run else True
    if plan.operation == "install" and not dry_run:
        payload["installed"] = True
    if plan.operation == "uninstall" and not dry_run:
        payload["uninstalled"] = True
        payload["preserved"] = list(plan.modified)
    return payload


def install_user(
    *,
    host: str | None = None,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
    install_dir: Path | None = None,
    source_root: Path | None = None,
    dry_run: bool = False,
    uninstall: bool = False,
) -> dict[str, Any]:
    """Install user-level files, or uninstall them when requested.

    This programmatic API applies a validated operation directly. The command
    line interface adds interactive confirmation before calling it.
    """

    if uninstall:
        return uninstall_user(
            host=host,
            skills_dir=skills_dir,
            bin_dir=bin_dir,
            install_dir=install_dir,
            dry_run=dry_run,
        )
    plan = build_install_plan(
        host=host,
        skills_dir=skills_dir,
        bin_dir=bin_dir,
        install_dir=install_dir,
        source_root=source_root,
    )
    if plan.is_blocked:
        raise InstallConflictError("Install plan contains conflicts", plan)
    if dry_run:
        return _completed_payload(plan, dry_run=True)
    changed = _apply_install_plan(plan)
    payload = _completed_payload(plan)
    payload["changedFiles"] = changed
    return payload


def uninstall_user(
    *,
    host: str | None = None,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
    install_dir: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Uninstall only unchanged files listed in the ownership manifest."""

    plan = build_uninstall_plan(
        host=host,
        skills_dir=skills_dir,
        bin_dir=bin_dir,
        install_dir=install_dir,
    )
    if plan.is_blocked:
        raise InstallConflictError("Uninstall plan contains conflicts", plan)
    if dry_run:
        return _completed_payload(plan, dry_run=True)
    changed = _apply_uninstall_plan(plan)
    payload = _completed_payload(plan)
    payload["changedFiles"] = changed
    return payload


def _print_human_plan(plan: OperationPlan) -> None:
    print(f"custom-openspec-install {plan.operation} plan")
    print(PROJECT_IDENTITY)
    for entry in plan.entries:
        suffix = f" ({entry.reason})" if entry.reason else ""
        print(f"{entry.operation}: {entry.path}{suffix}")
    if plan.prerequisites:
        print("prerequisites:")
        for prerequisite in plan.prerequisites:
            print(
                f"- {prerequisite.name} for {prerequisite.feature}: "
                f"{prerequisite.status}. Checked {prerequisite.checked}."
            )
            if prerequisite.resolved is not None:
                print(f"  found: {prerequisite.resolved}")
            if prerequisite.value:
                print(f"  value: {prerequisite.value}")
            if prerequisite.remediation:
                print(f"  warning: {prerequisite.remediation}")
    if plan.conflicts:
        print("conflicts:")
        for conflict in plan.conflicts:
            print(f"- {conflict}")


def _emit_payload(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        f"custom-openspec-install {payload.get('operation', 'operation')} "
        f"{payload.get('status', 'completed')}"
    )
    print(PROJECT_IDENTITY)
    for key, value in payload.items():
        if key in {"plan", "conflicts", "modified"}:
            continue
        print(f"{key}: {value}")
    if payload.get("conflicts"):
        print("conflicts:")
        for conflict in payload["conflicts"]:
            print(f"- {conflict}")


def _emit_json_plan(plan: OperationPlan) -> None:
    print(
        json.dumps(plan.to_dict(), indent=2, sort_keys=True),
        file=sys.stderr,
    )


def _confirm(plan: OperationPlan, *, as_json: bool) -> bool:
    prompt = f"Apply this {plan.operation} operation? [y/N] "
    if as_json:
        print(prompt, file=sys.stderr, end="", flush=True)
    else:
        _print_human_plan(plan)
        print(prompt, end="", flush=True)
    try:
        answer = input().strip().lower()
    except EOFError:
        return False
    return answer in {"y", "yes"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="custom-openspec-install",
        description=f"Install or uninstall the {PROJECT_IDENTITY} helpers for Codex.",
    )
    parser.add_argument("--host")
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--bin-dir", type=Path)
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("-y", "--yes", action="store_true", dest="yes")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def _plan_for_args(args: argparse.Namespace) -> OperationPlan:
    if args.uninstall:
        return build_uninstall_plan(
            host=args.host,
            skills_dir=args.skills_dir,
            bin_dir=args.bin_dir,
            install_dir=args.install_dir,
        )
    return build_install_plan(
        host=args.host,
        skills_dir=args.skills_dir,
        bin_dir=args.bin_dir,
        install_dir=args.install_dir,
        source_root=args.source_root,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        plan = _plan_for_args(args)
        payload = plan.to_dict(dry_run=args.dry_run)
        if plan.is_blocked:
            if not args.as_json:
                _print_human_plan(plan)
            payload["error"] = "Operation refused because the plan contains conflicts"
            _emit_payload(payload, as_json=args.as_json)
            return 2
        if args.dry_run:
            if not args.as_json:
                _print_human_plan(plan)
            _emit_payload(_completed_payload(plan, dry_run=True), as_json=args.as_json)
            return 0
        if args.as_json:
            _emit_json_plan(plan)
        if not args.yes:
            if not sys.stdin.isatty():
                if not args.as_json:
                    _print_human_plan(plan)
                payload["status"] = "blocked"
                payload["error"] = "Non-interactive input requires explicit -y or --yes confirmation bypass"
                _emit_payload(payload, as_json=args.as_json)
                return 2
            if not _confirm(plan, as_json=args.as_json):
                payload["status"] = "cancelled"
                payload["cancelled"] = True
                _emit_payload(payload, as_json=args.as_json)
                return 0
        elif not args.as_json:
            _print_human_plan(plan)
        if plan.operation == "install":
            changed = _apply_install_plan(plan)
        else:
            changed = _apply_uninstall_plan(plan)
        payload = _completed_payload(plan)
        payload["changedFiles"] = changed
        _emit_payload(payload, as_json=args.as_json)
        return 0
    except InstallConflictError as exc:
        payload = exc.plan.to_dict(dry_run=args.dry_run) if exc.plan is not None else {
            "operation": "uninstall" if args.uninstall else "install",
            "plan": [],
            "conflicts": [],
        }
        payload["status"] = "blocked"
        payload["error"] = str(exc)
        _emit_payload(payload, as_json=args.as_json)
        return 2
    except (InstallError, UnsupportedHostError) as exc:
        if args.as_json:
            print(json.dumps({"error": str(exc), "status": "error"}, indent=2, sort_keys=True))
        else:
            print(
                f"{PROJECT_IDENTITY}: custom-openspec-install refused the operation: {exc}",
                file=sys.stderr,
            )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
