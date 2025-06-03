#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from typing import Any, Dict, List, Sequence


NEW_PREFIX = "/github/workspace"


def _collect_paths(entries: Sequence[Dict[str, Any]]) -> List[str]:
    """Return every absolute file/dir path found in *entries*."""
    raw_paths = (
        value
        for entry in entries
        for value in (entry.get("directory"), entry.get("file"))
        if isinstance(value, str)  # guard against None / non-string
    )
    return [os.path.realpath(path) for path in raw_paths]


def patch_compile_commands(path: str) -> None:  # noqa: D401
    with open(path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    paths: List[str] = _collect_paths(data)
    if not paths:  # nothing to patch
        print("[WARN] compile_commands.json contained no absolute paths")
        return

    old_prefix = os.path.commonpath(paths)
    print(f"[INFO] Patching compile_commands.json: '{old_prefix}' → '{NEW_PREFIX}'")

    for entry in data:
        for key in ("file", "directory", "command"):
            val = entry.get(key)
            if (
                isinstance(val, str)
                and os.path.isabs(val)
                and val.startswith(old_prefix)
            ):
                entry[key] = val.replace(old_prefix, NEW_PREFIX, 1)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: patch_compile_commands.py <path-to-compile_commands.json>")
        sys.exit(1)

    patch_compile_commands(sys.argv[1])
