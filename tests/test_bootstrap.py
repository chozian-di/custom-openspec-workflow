from __future__ import annotations

import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import textwrap
import unittest

from custom_openspec.bootstrap import BootstrapError, NonStockSchemaError, bootstrap


FAKE_OPENSPEC = r'''#!/usr/bin/env python3
import json
from pathlib import Path
import sys

args = sys.argv[1:]
global_path = Path(__import__("os").environ["FAKE_OPENSPEC_GLOBAL"])
state = json.loads(global_path.read_text())

if args[:2] == ["config", "path"]:
    print(global_path)
elif args[:2] == ["config", "list"]:
    print(json.dumps(state))
elif args[:2] == ["config", "set"]:
    key, value = args[2], args[3]
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = value
    state[key] = parsed
    global_path.write_text(json.dumps(state))
elif args[0] == "init":
    target = Path(args[1])
    (target / "openspec").mkdir(parents=True, exist_ok=True)
    (target / "openspec" / "config.yaml").write_text("schema: spec-driven\n")
    (target / ".agents" / "skills" / "openspec-verify-change").mkdir(parents=True, exist_ok=True)
    (target / ".agents" / "skills" / "openspec-verify-change" / "SKILL.md").write_text("upstream verify\n")
elif args[0] == "update":
    target = Path(args[1])
    (target / ".agents" / "skills" / "openspec-verify-change").mkdir(parents=True, exist_ok=True)
    (target / ".agents" / "skills" / "openspec-verify-change" / "SKILL.md").write_text("upstream verify\n")
elif args[0] == "validate":
    if __import__("os").environ.get("FAKE_OPENSPEC_INVALID") == "1":
        print("validation failed", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({"valid": True}))
else:
    print("unknown fake command", file=sys.stderr)
    raise SystemExit(1)
'''


class BootstrapTests(unittest.TestCase):
    def fake_openspec(self, root: Path, invalid: bool = False) -> tuple[Path, Path]:
        executable = root / "fake-openspec"
        executable.write_text(FAKE_OPENSPEC, encoding="utf-8")
        executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
        global_path = root / "global.json"
        global_path.write_text(
            json.dumps(
                {
                    "profile": "core",
                    "delivery": "skills",
                    "workflows": [],
                }
            ),
            encoding="utf-8",
        )
        if invalid:
            import os

            os.environ["FAKE_OPENSPEC_INVALID"] = "1"
        else:
            import os

            os.environ.pop("FAKE_OPENSPEC_INVALID", None)
        return executable, global_path

    def test_new_and_repeated_setup_are_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "project"
            target.mkdir()
            (target / "keep.txt").write_text("user file\n", encoding="utf-8")
            executable, global_path = self.fake_openspec(root)
            import os

            os.environ["FAKE_OPENSPEC_GLOBAL"] = str(global_path)
            first = bootstrap(target, openspec_executable=str(executable))
            configuration = (target / "openspec" / "config.yaml").read_text(encoding="utf-8")
            second = bootstrap(target, openspec_executable=str(executable))
            self.assertTrue(first.verify_enabled)
            self.assertEqual(second.changed_entries, [])
            self.assertEqual(
                configuration,
                (target / "openspec" / "config.yaml").read_text(encoding="utf-8"),
            )
            self.assertEqual((target / "keep.txt").read_text(encoding="utf-8"), "user file\n")

    def test_non_stock_schema_is_refused_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "project"
            (target / "openspec").mkdir(parents=True)
            config = target / "openspec" / "config.yaml"
            config.write_text("schema: custom\nowner: user\n", encoding="utf-8")
            executable, global_path = self.fake_openspec(root)
            import os

            os.environ["FAKE_OPENSPEC_GLOBAL"] = str(global_path)
            with self.assertRaises(NonStockSchemaError):
                bootstrap(target, openspec_executable=str(executable))
            self.assertEqual(config.read_text(encoding="utf-8"), "schema: custom\nowner: user\n")

    def test_validation_failure_rolls_back_target_and_global_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "project"
            target.mkdir()
            executable, global_path = self.fake_openspec(root, invalid=True)
            import os

            os.environ["FAKE_OPENSPEC_GLOBAL"] = str(global_path)
            before_global = global_path.read_text(encoding="utf-8")
            with self.assertRaises(BootstrapError):
                bootstrap(target, openspec_executable=str(executable))
            self.assertFalse((target / "openspec" / "config.yaml").exists())
            self.assertEqual(global_path.read_text(encoding="utf-8"), before_global)
