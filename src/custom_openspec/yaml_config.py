"""Safe, conservative merging for an OpenSpec project configuration."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
import os
import tempfile
from typing import Any

import yaml


class ConfigurationError(ValueError):
    """The target configuration cannot be changed safely."""


@dataclass
class MergeResult:
    configuration: dict[str, Any]
    changes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def read_yaml_mapping(path: Path) -> dict[str, Any]:
    """Read one YAML object and reject malformed or non-object content."""

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConfigurationError(f"Cannot read {path}: {exc}") from exc

    try:
        value = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Cannot parse {path}: {exc}") from exc

    if not isinstance(value, dict):
        raise ConfigurationError(f"{path} must contain a YAML object")
    return value


def read_yaml_file(path: Path) -> dict[str, Any]:
    """Read a YAML object from a file, or return an empty object when absent."""

    if not path.exists():
        return {}
    return read_yaml_mapping(path)


def _string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ConfigurationError(f"{field_name} must be a list of strings")
    return value


def merge_policy(
    configuration: dict[str, Any], policy: dict[str, Any]
) -> MergeResult:
    """Merge only supported policy fields and retain all other project values."""

    result = deepcopy(configuration)
    changes: list[str] = []
    warnings: list[str] = []

    policy_rules = policy.get("rules", {})
    if not isinstance(policy_rules, dict):
        raise ConfigurationError("Policy rules must be a YAML object")
    policy_operations = policy.get("operations", {})
    if not isinstance(policy_operations, dict):
        raise ConfigurationError("Policy operations must be a YAML object")

    existing_rules = result.get("rules", {})
    if existing_rules is None:
        existing_rules = {}
    if not isinstance(existing_rules, dict):
        raise ConfigurationError("openspec/config.yaml rules must be a YAML object")
    result["rules"] = existing_rules

    for artifact_id, policy_entries in policy_rules.items():
        if not isinstance(artifact_id, str):
            raise ConfigurationError("Policy artifact IDs must be strings")
        policy_values = _string_list(policy_entries, f"Policy rules for {artifact_id}")
        current = existing_rules.get(artifact_id, [])
        current_values = _string_list(current, f"rules.{artifact_id}")
        seen: set[str] = set()
        for value in current_values:
            if value in seen:
                warnings.append(f"Existing duplicate retained: rules.{artifact_id}: {value}")
            seen.add(value)
        for value in policy_values:
            if value not in current_values:
                current_values.append(value)
                changes.append(f"rules.{artifact_id}: added policy entry")
        if current_values:
            existing_rules[artifact_id] = current_values

    existing_operations = result.get("operations", {})
    if existing_operations is None:
        existing_operations = {}
    if not isinstance(existing_operations, dict):
        raise ConfigurationError("openspec/config.yaml operations must be a YAML object")
    result["operations"] = existing_operations

    for operation_id, operation_policy in policy_operations.items():
        if not isinstance(operation_policy, dict):
            raise ConfigurationError(f"Policy operation {operation_id} must be a YAML object")
        policy_guidance = _string_list(
            operation_policy.get("guidance", []),
            f"Policy guidance for operations.{operation_id}",
        )
        current_operation = existing_operations.get(operation_id, {})
        if current_operation is None:
            current_operation = {}
        if not isinstance(current_operation, dict):
            raise ConfigurationError(f"operations.{operation_id} must be a YAML object")
        current_guidance = _string_list(
            current_operation.get("guidance", []),
            f"operations.{operation_id}.guidance",
        )
        seen = set()
        for value in current_guidance:
            if value in seen:
                warnings.append(
                    f"Existing duplicate retained: operations.{operation_id}.guidance: {value}"
                )
            seen.add(value)
        for value in policy_guidance:
            if value not in current_guidance:
                current_guidance.append(value)
                changes.append(f"operations.{operation_id}.guidance: added policy entry")
        current_operation["guidance"] = current_guidance
        existing_operations[operation_id] = current_operation

    return MergeResult(result, changes, warnings)


def serialize_yaml(configuration: dict[str, Any]) -> str:
    return yaml.safe_dump(
        configuration,
        sort_keys=False,
        default_flow_style=False,
        allow_unicode=True,
    )


def write_text_atomic(path: Path, content: str) -> None:
    """Write one file atomically and retain its existing mode when present."""

    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o644
    fd, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
