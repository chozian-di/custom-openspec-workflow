"""Command line support for the thin custom-openspec-grill adapter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Sequence

from .grill import (
    ExistingGrillContextError,
    GrillError,
    attach_session,
    compatibility_check,
    default_staging_dir,
    stage_source,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="custom-openspec-grill",
        description="Stage or attach delegated Grill Me context for OpenSpec.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    stage = subparsers.add_parser("stage", help="Stage an upstream Grill Me source file")
    stage.add_argument("--source", type=Path, required=True)
    stage.add_argument("--staging-dir", type=Path)
    stage.add_argument("--json", action="store_true", dest="as_json")

    attach = subparsers.add_parser("attach", help="Attach a staged session to an OpenSpec change")
    attach.add_argument("--root", type=Path, default=Path("."))
    attach.add_argument("--change", required=True)
    attach.add_argument("--session", required=True)
    attach.add_argument("--staging-dir", type=Path)
    attach.add_argument("--replace", action="store_true")
    attach.add_argument("--combine", action="store_true")
    attach.add_argument("--json", action="store_true", dest="as_json")

    compatibility = subparsers.add_parser("compatibility", help="Check the upstream Grill Me output contract")
    compatibility.add_argument("--source", type=Path, required=True)
    compatibility.add_argument("--staging-dir", type=Path)
    compatibility.add_argument(
        "--skills-dir",
        type=Path,
        help="Codex user-level skills directory used to discover grill-me",
    )
    compatibility.add_argument("--json", action="store_true", dest="as_json")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "stage":
            session = stage_source(args.source, args.staging_dir)
            payload = {
                "sessionId": session.session_id,
                "stagedSource": str(session.staged_source),
                "sourcePath": str(session.source_path),
                "sourceSha256": session.source_sha256,
                "stagingDir": str(session.staging_dir),
            }
        elif args.command == "attach":
            destination, changed = attach_session(
                args.root,
                args.change,
                args.session,
                staging_dir=args.staging_dir,
                replace=args.replace,
                combine=args.combine,
            )
            payload = {"destination": str(destination), "changed": changed}
        else:
            payload = compatibility_check(
                args.source,
                args.staging_dir,
                skills_dir=args.skills_dir,
            )

        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            for key, value in payload.items():
                print(f"{key}: {value}")
        if args.command == "compatibility" and payload.get("passed") is not True:
            reason = payload.get("failureReason") or payload.get("dependencyError")
            if reason:
                print(f"Compatibility evidence is incomplete: {reason}", file=sys.stderr)
            return 1
        return 0
    except ExistingGrillContextError as exc:
        print(f"custom-openspec-grill needs a user decision: {exc}", file=sys.stderr)
        return 2
    except GrillError as exc:
        print(f"custom-openspec-grill failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
