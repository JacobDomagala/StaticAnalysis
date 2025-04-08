#!/usr/bin/env python3
import json
import os
import sys

def patch_compile_commands(path, new_prefix=os.getenv("GITHUB_WORKSPACE")):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Infer old prefix from absolute file paths
    abs_paths = [entry["file"] for entry in data if os.path.isabs(entry["file"])]
    if not abs_paths:
        print("[INFO] No absolute file paths to patch.")
        return

    old_prefix = os.path.dirname(os.path.commonprefix(abs_paths)).rstrip("/")
    print(f"[INFO] Patching compile_commands.json: '{old_prefix}' → '{new_prefix}'")

    for entry in data:
        if os.path.isabs(entry["file"]) and entry["file"].startswith(old_prefix):
            entry["file"] = entry["file"].replace(old_prefix, new_prefix, 1)
        if os.path.isabs(entry["directory"]) and entry["directory"].startswith(old_prefix):
            entry["directory"] = entry["directory"].replace(old_prefix, new_prefix, 1)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: patch_compile_commands.py <path-to-compile_commands.json>")
        sys.exit(1)

    patch_compile_commands(sys.argv[1], sys.argv[2])
