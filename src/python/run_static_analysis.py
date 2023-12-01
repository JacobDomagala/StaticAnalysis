import argparse
import os
import sys
import json

import sa_utils as utils

def parse_pylint_json(pylint_json_in):
    with open(pylint_json_in, "r") as file:
        data = file.read()

    output_string=""
    try:
        pylint_data = json.loads(data)
        for item in pylint_data:
            output_string += f"{item['path']}:{item['line']}"
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

    line_prefix = f"{sa_utils.WORK_DIR}"

    return (
        pylint_file_name,
        output_to_console,
        common_ancestor,
        feature_branch,
        line_prefix,
    )


if __name__ == "__main__":
    print("starting ...")
    (
        pylint_file_name_in,
        output_to_console_in,
        common_ancestor_in,
        feature_branch_in,
        line_prefix_in,
    ) = parse_input_vars()
    issues_found = parse_pylint_json(pylint_file_name_in)
    sys.exit(issues_found)
