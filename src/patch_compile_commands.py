#!/usr/bin/env python3
import json
import os
import sys
import  itertools


def patch_compile_commands(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # collect every “directory” plus every “file” path
    paths = list(itertools.chain.from_iterable((e.get("directory"), e.get("file")) for e in data))
    paths = [os.path.realpath(p) for p in paths if p]# repo root on the host

    old_prefix = os.path.commonpath(paths)
    new_prefix = "/github/workspace"

    print(f"[INFO] Patching compile_commands.json: '{old_prefix}' → '{new_prefix}'")

    for entry in data:
        if os.path.isabs(entry["file"]) and entry["file"].startswith(old_prefix):
            entry["file"] = entry["file"].replace(old_prefix, new_prefix, 1)
        if os.path.isabs(entry["directory"]) and entry["directory"].startswith(old_prefix):
            entry["directory"] = entry["directory"].replace(old_prefix, new_prefix, 1)
        if os.path.isabs(entry["command"]) and entry["command"].startswith(old_prefix):
            entry["command"] = entry["command"].replace(old_prefix, new_prefix, 1)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: patch_compile_commands.py <path-to-compile_commands.json>")
        sys.exit(1)

    patch_compile_commands(sys.argv[1])
