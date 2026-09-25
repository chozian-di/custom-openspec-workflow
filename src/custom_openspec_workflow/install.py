"""Install the custom helper and skill into the supported user-level Codex paths."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Sequence

from .host import HostLayout, UnsupportedHostError, discover_host
from .paths import default_data_root


def _source_package_root() -> Path:
    return Path(__file__).resolve().parent


def _write_wrapper(path: Path, install_root: Path, module: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "#!/usr/bin/env python3\n" + (
        "import sys\n"
        f"sys.path.insert(0, {str(install_root)!r})\n"
        f"from {module} import main\n"
        "raise SystemExit(main())\n"
    )
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)
    path.chmod(0o755)


def install_user(
    *,
    host: str | None = None,
    skills_dir: Path | None = None,
    bin_dir: Path | None = None,
    install_dir: Path | None = None,
    source_root: Path | None = None,
    dry_run: bool = False,
) -> dict[str, str | bool]:
    selected_host = host or os.environ.get("CUSTOM_OPENSPEC_WORKFLOW_HOST", "codex")
    if selected_host.lower() != "codex":
        raise UnsupportedHostError(
            f"Unsupported host {selected_host!r}. This package supports Codex only."
        )
    if skills_dir is not None and bin_dir is not None:
        layout = HostLayout(
            "codex",
            skills_dir.expanduser().resolve(),
            bin_dir.expanduser().resolve(),
        )
    else:
        discovered = discover_host(selected_host)
        layout = HostLayout(
            "codex",
            (skills_dir or discovered.skills_dir).expanduser().resolve(),
            (bin_dir or discovered.bin_dir).expanduser().resolve(),
        )
    source_package = (source_root or _source_package_root()).expanduser().resolve()
    if not source_package.is_dir():
        raise UnsupportedHostError(f"Package source does not exist: {source_package}")
    destination = (
        install_dir if install_dir is not None else default_data_root()
    ).expanduser().resolve()
    skill_destination = layout.skills_dir / "custom-openspec-grill" / "SKILL.md"
    wrapper_names = {
        "custom-openspec-init": "custom_openspec_workflow.bootstrap",
        "custom-openspec-grill": "custom_openspec_workflow.grill_cli",
    }
    payload = {
        "host": layout.name,
        "skillsDir": str(layout.skills_dir),
        "binDir": str(layout.bin_dir),
        "installDir": str(destination),
        "skill": str(skill_destination),
        "dryRun": dry_run,
    }
    if dry_run:
        return payload

    destination.mkdir(parents=True, exist_ok=True)
    copied_package = destination / "custom_openspec_workflow"
    if copied_package.exists():
        shutil.rmtree(copied_package)
    shutil.copytree(source_package, copied_package)
    skill_destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_package / "data" / "custom-openspec-grill" / "SKILL.md", skill_destination)
    for name, module in wrapper_names.items():
        _write_wrapper(layout.bin_dir / name, destination, module)
    payload["installed"] = True
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="custom-openspec-install",
        description="Install the custom OpenSpec helpers for Codex.",
    )
    parser.add_argument("--host")
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--bin-dir", type=Path)
    parser.add_argument("--install-dir", type=Path)
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = install_user(
            host=args.host,
            skills_dir=args.skills_dir,
            bin_dir=args.bin_dir,
            install_dir=args.install_dir,
            source_root=args.source_root,
            dry_run=args.dry_run,
        )
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            print("custom-openspec-install completed")
            for key, value in payload.items():
                print(f"{key}: {value}")
        return 0
    except UnsupportedHostError as exc:
        print(f"custom-openspec-install refused the host: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
