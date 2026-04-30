#!/usr/bin/env python3
import json
import os
import sys

from typing import Any, Dict, List, Sequence, Tuple

DEFAULT_PREFIX = "/github/workspace"


def _collect_paths(
    entries: Sequence[Dict[str, Any]], keys: Sequence[str] = ("directory", "file")
) -> List[str]:
    return [
        os.path.normpath(v)
        for e in entries
        for key in keys
        for v in (e.get(key),)
        if isinstance(v, str)
    ]


def _new_prefix() -> str:
    return os.path.realpath(os.getenv("GITHUB_WORKSPACE", DEFAULT_PREFIX))


def _replace_prefixes(value: str, replacements: Sequence[Tuple[str, str]]) -> str:
    result = value
    for old_prefix, new_prefix in sorted(
        replacements, key=lambda replacement: len(replacement[0]), reverse=True
    ):
        if old_prefix in result:
            result = result.replace(old_prefix, new_prefix)
    return result


def patch_compile_commands(path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    all_paths = _collect_paths(data)
    directory_paths = _collect_paths(data, ("directory",))

    old_prefix = os.path.commonpath(all_paths)
    old_directory_prefix = (
        os.path.commonpath(directory_paths) if directory_paths else old_prefix
    )
    new_prefix = _new_prefix()
    new_directory_prefix = os.path.realpath(os.path.dirname(path))

    print(
        "[INFO] Patching compile_commands.json: "
        f"source '{old_prefix}' -> '{new_prefix}', "
        f"build '{old_directory_prefix}' -> '{new_directory_prefix}'"
    )

    command_replacements = (
        (old_directory_prefix, new_directory_prefix),
        (old_prefix, new_prefix),
    )

    for entry in data:
        file_value = entry.get("file")
        if isinstance(file_value, str):
            entry["file"] = _replace_prefixes(file_value, ((old_prefix, new_prefix),))

        directory_value = entry.get("directory")
        if isinstance(directory_value, str):
            entry["directory"] = _replace_prefixes(
                directory_value, ((old_directory_prefix, new_directory_prefix),)
            )

        command_value = entry.get("command")
        if isinstance(command_value, str):
            entry["command"] = _replace_prefixes(command_value, command_replacements)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: patch_compile_commands.py <compile_commands.json>")
    patch_compile_commands(sys.argv[1])
