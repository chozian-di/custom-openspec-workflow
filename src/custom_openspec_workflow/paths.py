"""Paths for package data and user-level installation."""

from __future__ import annotations

from importlib.resources import files
import os
from pathlib import Path


def default_data_root() -> Path:
    """Return the user-level data root for this project at call time."""

    return Path.home() / ".local" / "share" / "custom-openspec-workflow"


def default_cache_root() -> Path:
    """Return the user-level bytecode cache root for this project at call time."""

    return Path.home() / ".cache" / "custom-openspec-workflow"


def default_grill_staging_dir() -> Path:
    """Return the default Grill staging directory at call time."""

    configured = os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_GRILL_HOME")
    if configured:
        return Path(configured).expanduser()
    return default_data_root() / "grill"


def package_data_path(name: str) -> Path:
    """Return a package data path while running from the source tree or a wheel."""

    resource = files("custom_openspec_workflow").joinpath("data", name)
    return Path(resource)


def policy_path() -> Path:
    return package_data_path("openspec-policy.yaml")


def grill_skill_path() -> Path:
    return package_data_path("custom-openspec-grill/SKILL.md")
