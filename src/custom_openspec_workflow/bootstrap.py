"""Bootstrap a repository with the stock OpenSpec workflow and policy."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Sequence

from . import CORE_WORKFLOWS, PROJECT_IDENTITY, SUPPORTED_SCHEMA, VERIFY_WORKFLOW
from .paths import policy_path
from .yaml_config import (
    ConfigurationError,
    merge_policy,
    read_yaml_mapping,
    serialize_yaml,
    write_text_atomic,
)


class BootstrapError(RuntimeError):
    """A bootstrap operation failed and was rolled back."""


class NonStockSchemaError(BootstrapError):
    """The target uses a schema outside this package's compatibility boundary."""


@dataclass
class BootstrapResult:
    target: Path
    changed_files: list[str] = field(default_factory=list)
    changed_entries: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validation: str = "not-run"
    verify_enabled: bool = False
    rollback: bool = False


@dataclass
class FileState:
    content: bytes
    mode: int


def _file_snapshot(root: Path) -> dict[Path, FileState]:
    if not root.exists():
        return {}
    if root.is_file():
        stat = root.stat()
        return {root: FileState(root.read_bytes(), stat.st_mode & 0o777)}
    state: dict[Path, FileState] = {}
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            stat = path.stat()
            state[path] = FileState(path.read_bytes(), stat.st_mode & 0o777)
    return state


def _restore_files(before: dict[Path, FileState], roots: Sequence[Path]) -> None:
    current_files: set[Path] = set()
    for root in roots:
        if root.is_file():
            current_files.add(root)
        elif root.exists():
            current_files.update(
                path for path in root.rglob("*") if path.is_file() and not path.is_symlink()
            )

    for path in sorted(current_files - before.keys(), key=lambda item: len(item.parts), reverse=True):
        try:
            path.unlink()
        except FileNotFoundError:
            pass

    for path, state in before.items():
        if path.is_file():
            current = FileState(path.read_bytes(), path.stat().st_mode & 0o777)
            if current == state:
                continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(state.content)
        os.chmod(path, state.mode)

    for root in sorted(roots, key=lambda item: len(item.parts), reverse=True):
        if root.is_dir():
            for directory in sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True):
                if directory.is_dir() and not directory.is_symlink():
                    try:
                        directory.rmdir()
                    except OSError:
                        pass


def _parse_json(output: str, description: str) -> Any:
    try:
        return json.loads(output)
    except json.JSONDecodeError as exc:
        raise BootstrapError(f"{description} did not return JSON: {exc}") from exc


class OpenSpecRunner:
    def __init__(self, executable: str = "openspec") -> None:
        self.executable = executable

    def run(self, arguments: Sequence[str], cwd: Path) -> subprocess.CompletedProcess[str]:
        command = [self.executable, *arguments]
        try:
            return subprocess.run(
                command,
                cwd=cwd,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
        except OSError as exc:
            raise BootstrapError(f"Cannot run {' '.join(command)}: {exc}") from exc

    def require(self, arguments: Sequence[str], cwd: Path, action: str) -> str:
        result = self.run(arguments, cwd)
        if result.returncode != 0:
            detail = (result.stderr or result.stdout).strip()
            raise BootstrapError(f"{action} failed: {detail or 'unknown error'}")
        return result.stdout

    def global_config_path(self, cwd: Path) -> Path:
        output = self.require(["config", "path"], cwd, "OpenSpec global configuration path lookup")
        path_text = output.strip().splitlines()[-1] if output.strip() else ""
        if not path_text:
            raise BootstrapError("OpenSpec did not report a global configuration path")
        return Path(path_text).expanduser().resolve()

    def global_config(self, cwd: Path) -> dict[str, Any]:
        output = self.require(["config", "list", "--json"], cwd, "OpenSpec global configuration lookup")
        value = _parse_json(output, "OpenSpec global configuration lookup")
        if not isinstance(value, dict):
            raise BootstrapError("OpenSpec global configuration is not an object")
        return value

    def set_global(self, key: str, value: str, cwd: Path) -> None:
        self.require(["config", "set", key, value], cwd, f"Set OpenSpec global {key}")


def _effective_workflows(global_config: dict[str, Any]) -> list[str]:
    if global_config.get("profile", "core") == "custom":
        workflows = global_config.get("workflows", [])
        if isinstance(workflows, list) and all(isinstance(item, str) for item in workflows):
            return list(dict.fromkeys(workflows))
        return []
    return list(CORE_WORKFLOWS)


def _ensure_verify_profile(
    runner: OpenSpecRunner,
    cwd: Path,
    global_config: dict[str, Any],
    result: BootstrapResult,
    *,
    dry_run: bool = False,
) -> bool:
    workflows = _effective_workflows(global_config)
    profile = global_config.get("profile", "core")
    needs_profile = profile != "custom" or VERIFY_WORKFLOW not in workflows
    if needs_profile:
        desired = list(dict.fromkeys([*workflows, VERIFY_WORKFLOW]))
        if not dry_run:
            runner.set_global("profile", "custom", cwd)
            runner.set_global("workflows", json.dumps(desired, separators=(",", ":")), cwd)
        result.changed_entries.extend(["global.profile: custom", "global.workflows: added verify"])

    delivery = global_config.get("delivery", "both")
    if delivery == "commands":
        if not dry_run:
            runner.set_global("delivery", "both", cwd)
        result.changed_entries.append("global.delivery: both for Codex skills")
    return True


def _target_has_verify_skill(target: Path) -> bool:
    return (target / ".agents" / "skills" / "openspec-verify-change" / "SKILL.md").is_file()


def _validate_target(runner: OpenSpecRunner, target: Path) -> None:
    output = runner.require(
        ["validate", "--all", "--json", "--no-interactive"],
        target,
        "OpenSpec validation",
    )
    _parse_json(output, "OpenSpec validation")


def _rollback(
    target_before: dict[Path, FileState],
    target_roots: Sequence[Path],
    global_before: dict[Path, FileState],
    global_path: Path | None,
) -> None:
    _restore_files(target_before, target_roots)
    if global_path is not None:
        _restore_files(global_before, [global_path])


def bootstrap(
    target: Path,
    *,
    tools: str = "codex",
    openspec_executable: str = "openspec",
    policy: Path | None = None,
    dry_run: bool = False,
) -> BootstrapResult:
    """Prepare one repository and roll back all owned changes on failure."""

    target = target.expanduser().resolve()
    if not target.is_dir():
        raise BootstrapError(f"Target is not a directory: {target}")
    if tools.lower() != "codex":
        raise BootstrapError(
            f"Unsupported OpenSpec host selection {tools!r}. This package supports Codex only."
        )

    runner = OpenSpecRunner(openspec_executable)
    config_path = target / "openspec" / "config.yaml"
    openspec_dir = target / "openspec"
    snapshots_ready = False

    if config_path.exists():
        try:
            existing = read_yaml_mapping(config_path)
        except ConfigurationError as exc:
            raise BootstrapError(str(exc)) from exc
        schema = existing.get("schema")
        if schema != SUPPORTED_SCHEMA:
            raise NonStockSchemaError(
                f"Target uses schema {schema!r}. This package only supports "
                f"the stock {SUPPORTED_SCHEMA!r} schema. No files were changed."
            )
    elif openspec_dir.exists():
        raise BootstrapError(
            f"{openspec_dir} exists without config.yaml. Refusing to classify or replace it."
        )

    try:
        global_path = runner.global_config_path(target)
        global_before = _file_snapshot(global_path)
        target_roots = [target / "openspec", target / ".agents"]
        target_before: dict[Path, FileState] = {}
        for root in target_roots:
            target_before.update(_file_snapshot(root))
        snapshots_ready = True

        global_config = runner.global_config(target)
        result = BootstrapResult(target)
        verify_enabled = _ensure_verify_profile(
            runner,
            target,
            global_config,
            result,
            dry_run=dry_run,
        )

        if dry_run:
            result.verify_enabled = verify_enabled
            result.validation = "skipped in dry-run"
            return result

        is_new = not openspec_dir.exists()
        if is_new:
            runner.require(
                [
                    "init",
                    str(target),
                    "--tools",
                    tools,
                    "--profile",
                    "custom",
                    "--no-animation",
                ],
                target,
                "OpenSpec initialization",
            )
            result.changed_files.append("normal OpenSpec initialization output")
        elif not _target_has_verify_skill(target):
            runner.require(
                [
                    "init",
                    str(target),
                    "--tools",
                    tools,
                    "--profile",
                    "custom",
                    "--no-animation",
                ],
                target,
                "additive OpenSpec initialization",
            )
            result.changed_files.append("additive normal OpenSpec initialization output")

        if not config_path.is_file():
            raise BootstrapError(f"OpenSpec did not create {config_path}")
        configuration = read_yaml_mapping(config_path)
        if configuration.get("schema") != SUPPORTED_SCHEMA:
            raise NonStockSchemaError(
                f"OpenSpec produced schema {configuration.get('schema')!r}. "
                f"Expected {SUPPORTED_SCHEMA!r}."
            )
        policy_path_value = policy or policy_path()
        policy_configuration = read_yaml_mapping(policy_path_value)
        merged = merge_policy(configuration, policy_configuration)
        if merged.changes:
            write_text_atomic(config_path, serialize_yaml(merged.configuration))
            result.changed_files.append(str(config_path))
        result.changed_entries.extend(merged.changes)
        result.warnings.extend(merged.warnings)

        _validate_target(runner, target)
        current_global = runner.global_config(target)
        current_workflows = _effective_workflows(current_global)
        if VERIFY_WORKFLOW not in current_workflows:
            raise BootstrapError("The selected OpenSpec profile does not include verify")
        if not _target_has_verify_skill(target):
            raise BootstrapError(
                "OpenSpec Verify is enabled in the profile but the Codex Verify skill is missing"
            )
        result.verify_enabled = True
        result.validation = "passed"

        after_files = set()
        for root in target_roots:
            after_files.update(_file_snapshot(root).keys())
        before_files = set(target_before)
        for path in sorted(after_files - before_files):
            if str(path) not in result.changed_files:
                result.changed_files.append(str(path))
        if global_path.exists() and global_before.get(global_path) != FileState(
            global_path.read_bytes(), global_path.stat().st_mode & 0o777
        ):
            result.changed_files.append(str(global_path))
        return result
    except Exception as exc:
        if not snapshots_ready:
            if isinstance(exc, BootstrapError):
                raise
            raise BootstrapError(f"Bootstrap failed before changes began: {exc}") from exc
        try:
            _rollback(
                locals().get("target_before", {}),
                locals().get("target_roots", [target / "openspec", target / ".agents"]),
                locals().get("global_before", {}),
                locals().get("global_path"),
            )
        except Exception as rollback_exc:
            raise BootstrapError(
                f"{exc}. Rollback also failed: {rollback_exc}"
            ) from exc
        if isinstance(exc, BootstrapError):
            raise BootstrapError(f"{exc} Rollback completed.") from exc
        if isinstance(exc, ConfigurationError):
            raise BootstrapError(f"{exc} Rollback completed.") from exc
        raise BootstrapError(f"Bootstrap failed: {exc}. Rollback completed.") from exc


def _print_result(result: BootstrapResult, as_json: bool) -> None:
    payload = {
        "target": str(result.target),
        "changedFiles": result.changed_files,
        "changedEntries": result.changed_entries,
        "warnings": result.warnings,
        "validation": result.validation,
        "verifyEnabled": result.verify_enabled,
        "rollback": result.rollback,
    }
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    print(f"custom-openspec-init completed for {result.target}")
    print(f"Validation: {result.validation}")
    print(f"Verify enabled: {'yes' if result.verify_enabled else 'no'}")
    print("Changed files:")
    for item in result.changed_files:
        print(f"- {item}")
    print("Changed configuration entries:")
    for item in result.changed_entries:
        print(f"- {item}")
    for warning in result.warnings:
        print(f"Warning: {warning}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="custom-openspec-init",
        description=f"Add the user-level policy for {PROJECT_IDENTITY} to a stock OpenSpec repository.",
    )
    parser.add_argument("path", nargs="?", default=".", help="Repository path")
    parser.add_argument("--tools", default="codex", help="Tools passed to openspec init")
    parser.add_argument("--openspec-executable", default="openspec")
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = bootstrap(
            Path(args.path),
            tools=args.tools,
            openspec_executable=args.openspec_executable,
            policy=args.policy,
            dry_run=args.dry_run,
        )
        _print_result(result, args.as_json)
        return 0
    except NonStockSchemaError as exc:
        print(f"custom-openspec-init refused the target: {exc}", file=sys.stderr)
        return 2
    except BootstrapError as exc:
        print(f"custom-openspec-init failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
