"""User-level customization for the stock OpenSpec workflow."""

PACKAGE_NAME = "custom-openspec-workflow"
PACKAGE_VERSION = "0.1.0"
SUPPORTED_HOST = "codex"
SUPPORTED_SCHEMA = "spec-driven"
VERIFY_WORKFLOW = "verify"

CORE_WORKFLOWS = (
    "propose",
    "explore",
    "apply",
    "update",
    "sync",
    "archive",
)
