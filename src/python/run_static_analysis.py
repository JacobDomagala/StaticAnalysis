import argparse
import os
import sys
import subprocess
import re
from github import Github
import json

# Input variables from Github action
GITHUB_TOKEN = os.getenv("INPUT_GITHUB_TOKEN")
PR_NUM = os.getenv("INPUT_PR_NUM")
WORK_DIR = f'{os.getenv("GITHUB_WORKSPACE")}'
REPO_NAME = os.getenv("INPUT_REPO")
TARGET_REPO_NAME = os.getenv("INPUT_REPO")
SHA = os.getenv("GITHUB_SHA")
COMMENT_TITLE = os.getenv("INPUT_COMMENT_TITLE")
ONLY_PR_CHANGES = os.getenv("INPUT_REPORT_PR_CHANGES_ONLY", "False").lower()
VERBOSE = os.getenv("INPUT_VERBOSE", "False").lower() == "true"
FILES_WITH_ISSUES = {}

# Max characters per comment - 65536
# Make some room for HTML tags and error message
MAX_CHAR_COUNT_REACHED = (
    "!Maximum character count per GitHub comment has been reached!"
    " Not all warnings/errors has been parsed!"
)
COMMENT_MAX_SIZE = 65000
CURRENT_COMMENT_LENGTH = 0


def debug_print(message):
    if VERBOSE:
        lines = message.split("\n")
        for line in lines:
            print(f"\033[96m {line}")


def parse_pylint_json(pylint_json_in):

    with open(pylint_json_in, "r") as file:
        data = file.read()

    try:
        pylint_data = json.loads(data)
        for item in pylint_data:
            print("Type:", item["type"])
            print("Module:", item["module"])
            print("Object:", item["obj"])
            print("Line:", item["line"])
            print("Column:", item["column"])
            print("End Line:", item["endLine"])
            print("End Column:", item["endColumn"])
            print("Path:", item["path"])
            print("Symbol:", item["symbol"])
            print("Message:", item["message"])
            print("Message ID:", item["message-id"])

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")

    return 0


def parse_input_vars():
    # Get cppcheck and clang-tidy files
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-pl", "--pylint", help="Output file name for pylint", required=True
    )
    parser.add_argument(
        "-o",
        "--output_to_console",
        help="Whether to output the result to console",
        required=True,
    )
    parser.add_argument(
        "-fk",
        "--fork_repository",
        help="Whether the actual code is in 'pr_tree' directory",
        required=True,
    )
    parser.add_argument(
        "--common",
        default="",
        help="common ancestor between two branches (default: %(default)s)",
    )
    parser.add_argument("--head", default="", help="Head branch (default: %(default)s)")
    if parser.parse_args().fork_repository == "true":
        global REPO_NAME

        # Make sure to use Head repository
        REPO_NAME = os.getenv("INPUT_PR_REPO")

    pylint_file_name = parser.parse_args().pylint
    output_to_console = parser.parse_args().output_to_console == "true"

    common_ancestor = parser.parse_args().common
    feature_branch = parser.parse_args().head

    line_prefix = f"{WORK_DIR}"
    return (
        pylint_file_name,
        output_to_console,
        common_ancestor,
        feature_branch,
        line_prefix,
    )


if __name__ == "__main__":
    (
        pylint_file_name_in,
        output_to_console_in,
        common_ancestor_in,
        feature_branch_in,
        line_prefix_in,
    ) = parse_input_vars()
    issues_found = parse_pylint_json(pylint_file_name_in)
    sys.exit(issues_found)
