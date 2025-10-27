#!/usr/bin/env python3

import argparse
import difflib
import re
import sys
from pathlib import Path

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
LOG_PREFIX_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T[0-9:.]+Z\s+")
SHA_PATTERN = re.compile(
    r"(https://github\.com/[^/]+/[^/]+/blob/)[0-9a-f]{40}(/)"
)
REPORT_MARKER = "##[error] Issues found!"
RESULT_LABELS = (
    "cppcheck results:",
    "clang-tidy results:",
    "PyLint results:",
)
CPP_ISSUE_PATTERN = re.compile(
    r"^(?P<path>/.+?):(?P<line>\d+):(?:\d+:)?\s+"
    r"(?P<level>error|warning|style|performance|portability|information|note):\s+"
    r"(?P<message>.+)$"
)
PYTHON_ISSUE_PATTERN = re.compile(
    r"^(?P<path>.+?\.py):(?P<line>\d+):?\s+(?P<message>[A-Z]\d{4}:.+)$"
)


def _split_inline_result_label(line: str) -> list[str]:
    for label in RESULT_LABELS:
        if line.startswith(label):
            remainder = line[len(label):].strip()
            return [label, remainder] if remainder else [label]
    return [line]


def _canonical_issue_line(line: str) -> str | None:
    match = CPP_ISSUE_PATTERN.match(line)
    if match:
        return (
            f"{match.group('path')}:{match.group('line')}: "
            f"{match.group('level')}: {match.group('message')}"
        )

    match = PYTHON_ISSUE_PATTERN.match(line)
    if match:
        return f"{match.group('path')}:{match.group('line')}: {match.group('message')}"

    return None


def normalize_console_output(output: str) -> str:
    normalized = ANSI_PATTERN.sub("", output)
    marker_index = normalized.rfind(REPORT_MARKER)
    if marker_index == -1:
        raise RuntimeError(f"Console output does not contain '{REPORT_MARKER}'")

    normalized = normalized[marker_index:]
    normalized = SHA_PATTERN.sub(r"\1<SHA>\2", normalized)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

    lines: list[str] = []
    for original_line in normalized.split("\n"):
        original_line = LOG_PREFIX_PATTERN.sub("", original_line)
        for line in _split_inline_result_label(original_line.strip()):
            if not line:
                continue

            if line == REPORT_MARKER or line in RESULT_LABELS:
                lines.append(line)
                continue

            issue_line = _canonical_issue_line(line)
            if issue_line is not None:
                lines.append(issue_line)

    return "\n".join(lines).strip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", required=True)
    parser.add_argument("--fixture", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    actual = normalize_console_output(Path(args.log).read_text(encoding="utf-8"))
    expected = normalize_console_output(Path(args.fixture).read_text(encoding="utf-8"))

    if actual == expected:
        print(f"Console output matches fixture: {args.fixture}")
        return 0

    diff = difflib.unified_diff(
        expected.splitlines(),
        actual.splitlines(),
        fromfile=args.fixture,
        tofile=args.log,
        lineterm="",
    )
    print("\n".join(diff))
    return 1


if __name__ == "__main__":
    sys.exit(main())
