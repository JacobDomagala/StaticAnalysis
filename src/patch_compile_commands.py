#!/usr/bin/env python3
"""
Rewrite absolute host paths inside a compile_commands.json so that
they point to /github/workspace (or a user-supplied prefix).

• Patches the `file`, `directory` fields
• Rewrites *every* token in a `command` string
• Rewrites each element of an `arguments` array (used by Ninja/MSBuild)
• Leaves relative paths untouched
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import sys
from itertools import chain
from pathlib import Path
from typing import Any, Dict, List

# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #


def detect_common_prefix(entries: List[Dict[str, Any]]) -> str:
    """Find the longest common absolute prefix among every file & directory."""
    paths = list(
        chain.from_iterable((e.get("directory"), e.get("file")) for e in entries)
    )
    # discard None, resolve symlinks & '..'
    paths = [os.path.realpath(p) for p in paths if p]
    return os.path.commonpath(paths) if paths else "/"


def patch_token(token: str, old: str, new: str) -> str:
    """Rewrite a single token if it begins with the old prefix."""
    return token.replace(old, new, 1) if token.startswith(old) else token


def patch_entry(entry: Dict[str, Any], old: str, new: str) -> None:
    """Patch every relevant field inside one compile_commands entry."""
    for key in ("file", "directory"):
        if key in entry:
            entry[key] = patch_token(entry[key], old, new)

    # A) compile_commands.json variant with a single 'command' string
    if "command" in entry:
        toks = shlex.split(entry["command"])
        toks = [patch_token(t, old, new) for t in toks]
        entry["command"] = " ".join(shlex.quote(t) for t in toks)

    # B) variant with an 'arguments' array
    if "arguments" in entry and isinstance(entry["arguments"], list):
        entry["arguments"] = [patch_token(a, old, new) for a in entry["arguments"]]


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Rewrite absolute paths inside compile_commands.json"
    )
    parser.add_argument(
        "compile_commands",
        type=Path,
        help="Path to compile_commands.json",
    )
    parser.add_argument(
        "--new-prefix",
        default="/github/workspace",
        help="Prefix that should replace the host path (default: /github/workspace)",
    )
    args = parser.parse_args()

    with args.compile_commands.open(encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    old_prefix = detect_common_prefix(data)
    new_prefix = args.new_prefix.rstrip("/")

    if not old_prefix:
        sys.exit("[ERROR] Could not determine a common path prefix to rewrite.")

    print(f"[INFO] Patching compile_commands.json: '{old_prefix}' → '{new_prefix}'")

    for entry in data:
        patch_entry(entry, old_prefix, new_prefix)

    with args.compile_commands.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")  # POSIX-friendly final newline


# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
