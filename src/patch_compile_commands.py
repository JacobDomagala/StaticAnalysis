#!/usr/bin/env python3
import json
import os
import sys

from typing import Any, Dict, List, Sequence

DEFAULT_PREFIX = "/github/workspace"


def _collect_paths(entries: Sequence[Dict[str, Any]]) -> List[str]:
    return [
        os.path.realpath(v)
        for e in entries
        for v in (e.get("directory"), e.get("file"))
        if isinstance(v, str)
    ]


def _new_prefix() -> str:
    return os.path.realpath(os.getenv("GITHUB_WORKSPACE", DEFAULT_PREFIX))


def patch_compile_commands(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    old_prefix = os.path.commonpath(_collect_paths(data))
    new_prefix = _new_prefix()
    print(f"[INFO] Patching compile_commands.json: '{old_prefix}' → '{new_prefix}'")
    for entry in data:
        for key in ("file", "directory", "command"):
            val = entry.get(key)
            if isinstance(val, str) and old_prefix in val:
                entry[key] = val.replace(old_prefix, new_prefix)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: patch_compile_commands.py <compile_commands.json>")
    patch_compile_commands(sys.argv[1])
