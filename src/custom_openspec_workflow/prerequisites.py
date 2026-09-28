"""Shared guidance for external OpenSpec prerequisites."""

from __future__ import annotations


OPENSPEC_INSTALL_COMMAND = "npm install -g @fission-ai/openspec@latest"
OPENSPEC_VERSION_COMMAND = "openspec --version"
OPENSPEC_EXECUTABLE_OVERRIDE = "--openspec-executable /path/to/openspec"


def openspec_install_guidance() -> str:
    """Return the external installation steps for a missing OpenSpec command."""

    return (
        "Install OpenSpec outside this project with:\n"
        f"  {OPENSPEC_INSTALL_COMMAND}\n"
        f"  {OPENSPEC_VERSION_COMMAND}\n"
        f"If the executable is outside PATH, pass `{OPENSPEC_EXECUTABLE_OVERRIDE}` "
        "to `custom-openspec-init`. This package does not install OpenSpec."
    )


def missing_openspec_message(selected_executable: str = "openspec") -> str:
    """Return actionable guidance for an unavailable selected executable."""

    return (
        f"OpenSpec executable `{selected_executable}` is not available. "
        "This workflow cannot function until OpenSpec is installed. "
        + openspec_install_guidance()
    )


def missing_openspec_acknowledgment_prompt() -> str:
    """Return the install prompt used when OpenSpec is missing."""

    return (
        "OpenSpec is missing. This workflow cannot function until OpenSpec is installed. "
        "Continue with package installation? [y/N] "
    )
