"""User-level customization for the stock OpenSpec workflow."""

PACKAGE_NAME = "custom-openspec-workflow"
PROJECT_SHORT_NAME = "COW"
PROJECT_ALTERNATE_NAME = "chozian's OpenSpec Workflow"
PROJECT_IDENTITY = (
    f'{PACKAGE_NAME} ({PROJECT_SHORT_NAME}, also known as "{PROJECT_ALTERNATE_NAME}")'
)
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
