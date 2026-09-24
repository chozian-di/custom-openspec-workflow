"""Paths for package data and user-level installation."""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path


def package_data_path(name: str) -> Path:
    """Return a package data path while running from the source tree or a wheel."""

    resource = files("custom_openspec").joinpath("data", name)
    return Path(resource)


def policy_path() -> Path:
    return package_data_path("openspec-policy.yaml")


def grill_skill_path() -> Path:
    return package_data_path("custom-openspec-grill/SKILL.md")
