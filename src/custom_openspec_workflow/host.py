"""Host discovery for the supported Codex user-level integration."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import shutil

from . import SUPPORTED_HOST


class UnsupportedHostError(RuntimeError):
    """The package cannot identify a supported host location."""


@dataclass(frozen=True)
class HostLayout:
    name: str
    skills_dir: Path
    bin_dir: Path


def _candidate_skills_dirs() -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.append(Path.home() / ".agents" / "skills")
    return list(dict.fromkeys(candidates))


def _candidate_bin_dirs() -> list[Path]:
    candidates: list[Path] = []
    configured = os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR")
    if configured:
        candidates.append(Path(configured).expanduser())
    for item in os.environ.get("PATH", "").split(os.pathsep):
        if item:
            candidates.append(Path(item).expanduser())
    return list(dict.fromkeys(candidates))


def discover_host(host: str | None = None) -> HostLayout:
    """Discover Codex locations without selecting another host layout."""

    selected = host or os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_HOST")
    if selected and selected.lower() != SUPPORTED_HOST:
        raise UnsupportedHostError(
            f"Unsupported host {selected!r}. This package supports Codex only."
        )

    skills_dir = next(
        (candidate for candidate in _candidate_skills_dirs() if candidate.exists()),
        None,
    )
    if skills_dir is None:
        raise UnsupportedHostError(
            "Codex was not detected. Set CUSTOM_OPENSPEC_WORKFLOW_SKILLS_DIR to the existing "
            "user-level .agents/skills directory or pass --skills-dir."
        )

    bin_dir = next(
        (
            candidate
            for candidate in _candidate_bin_dirs()
            if candidate.is_dir() and os.access(candidate, os.W_OK)
        ),
        None,
    )
    if bin_dir is None:
        raise UnsupportedHostError(
            "No writable user-level executable directory was found in PATH. "
            "Set CUSTOM_OPENSPEC_WORKFLOW_BIN_DIR to a writable directory in PATH."
        )
    return HostLayout(SUPPORTED_HOST, skills_dir, bin_dir)


def validate_explicit_layout(
    host: str,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
) -> HostLayout:
    if host.lower() != SUPPORTED_HOST:
        raise UnsupportedHostError(
            f"Unsupported host {host!r}. This package supports Codex only."
        )
    discovered = discover_host(host)
    chosen_skills = (skills_dir or discovered.skills_dir).expanduser()
    chosen_bin = (bin_dir or discovered.bin_dir).expanduser()
    if not chosen_skills.is_absolute() or not chosen_bin.is_absolute():
        raise UnsupportedHostError("Host paths must be absolute")
    return HostLayout(host.lower(), chosen_skills, chosen_bin)


def executable_in_path(name: str) -> Path | None:
    return Path(shutil.which(name)).resolve() if shutil.which(name) else None
