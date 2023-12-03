import os
import sys
import json

from . import sa_utils as utils


def parse_pylint_json(
    pylint_json_in, output_to_console, common_ancestor, feature_branch
):
    with open(pylint_json_in, "r", encoding="utf-8") as file:
        data = file.read()

    files_changed_in_pr = {}
    if not output_to_console and (utils.ONLY_PR_CHANGES == "true"):
        files_changed_in_pr = utils.get_changed_files(common_ancestor, feature_branch)

    pylint_comment_out, pylint_issues_found_out = create_comment_for_output(
        json.loads(data), files_changed_in_pr, output_to_console
    )

    if output_to_console and pylint_issues_found_out:
        print("##[error] Issues found!\n")
        error_color = "\u001b[31m"
        print(f"{error_color}PyLint results: {pylint_comment_out}")

    return pylint_comment_out, pylint_issues_found_out


def parse_input_vars():
    parser = utils.create_common_input_vars_parser()
    parser.add_argument(
        "-pl", "--pylint", help="Output file name for pylint", required=True
    )

    if parser.parse_args().fork_repository == "true":
        # Make sure to use Head repository
        utils.REPO_NAME = os.getenv("INPUT_PR_REPO")

    pylint_file_name = parser.parse_args().pylint
    output_to_console = parser.parse_args().output_to_console == "true"

    common_ancestor = parser.parse_args().common
    feature_branch = parser.parse_args().head

    return (pylint_file_name, output_to_console, common_ancestor, feature_branch)


def append_issue(is_note, per_issue_string, new_line, list_of_issues):
    if not is_note:
        if len(per_issue_string) > 0 and (per_issue_string not in list_of_issues):
            list_of_issues.append(per_issue_string)
        per_issue_string = new_line
    else:
        per_issue_string += new_line

    return per_issue_string


def create_comment_for_output(tool_output, files_changed_in_pr, output_to_console):
    """
    Generates a comment for a GitHub pull request based on the tool output.

    Parameters:
        tool_output (str): The tool output to parse.
        prefix (str): The prefix to look for in order to identify issues.
        files_changed_in_pr (dict): A dictionary containing the files that were
            changed in the pull request and the lines that were modified.
        output_to_console (bool): Whether or not to output the results to the console.

    Returns:
        tuple: A tuple containing the generated comment and the number of issues found.
    """

    list_of_issues = []
    per_issue_string = ""

    for line in tool_output:
        file_path = line["path"]
        file_line_start = line["line"]
        issue_description = (
            f"{line['message-id']}: {line['message']} ({line['symbol']})"
        )

        file_line_end = utils.get_file_line_end(file_path, file_line_start)

        # In case where we only output to console, skip the next part
        if output_to_console:
            per_issue_string = append_issue(
                False,
                per_issue_string,
                f"{file_path}:{file_line_start} {issue_description}",
                list_of_issues,
            )
            continue

        if utils.is_part_of_pr_changes(file_path, file_line_start, files_changed_in_pr):
            per_issue_string, description = utils.generate_description(
                False,
                False,
                file_line_start,
                issue_description,
                per_issue_string,
            )

            new_line = utils.generate_output(
                False, file_path, file_line_start, file_line_end, description
            )

            if utils.check_for_char_limit(new_line):
                per_issue_string = append_issue(
                    False, per_issue_string, new_line, list_of_issues
                )
                utils.CURRENT_COMMENT_LENGTH += len(new_line)

            else:
                utils.CURRENT_COMMENT_LENGTH = utils.COMMENT_MAX_SIZE

                return "\n".join(list_of_issues), len(list_of_issues)

    # Append any unprocessed issues
    if len(per_issue_string) > 0 and (per_issue_string not in list_of_issues):
        list_of_issues.append(per_issue_string)

    output_string = "\n".join(list_of_issues)

    utils.debug_print(f"\nFinal output_string = \n{output_string}\n")

    return output_string, len(list_of_issues)


def prepare_comment_body(pylint_comment_in, pylint_issues_found_in):
    """
    Generates a comment body based on the results of the PyLint analysis.

    Args:
        pylint_comment (str): The comment body generated for the PyLint analysis.
        pylint_issues_found (int): The number of issues found by PyLint analysis.

    Returns:
        str: The final comment body that will be posted as a comment on the pull request.
    """

    if pylint_issues_found_in == 0:
        full_comment_body = (
            '## <p align="center"><b> :white_check_mark:'
            f"{utils.COMMENT_TITLE} - no issues found! :white_check_mark: </b></p>"
        )
    else:
        full_comment_body = (
            f'## <p align="center"><b> :zap: {utils.COMMENT_TITLE} :zap: </b></p> \n\n'
        )

        full_comment_body += (
            f"<details> <summary> <b> :red_circle: PyLint found "
            f"{pylint_issues_found_in} {'issues' if pylint_issues_found_in > 1 else 'issue'}!"
            " Click here to see details. </b> </summary> <br>"
            f"{pylint_comment_in} </details>"
        )

        full_comment_body += "\n\n *** \n"

    if utils.CURRENT_COMMENT_LENGTH == utils.COMMENT_MAX_SIZE:
        full_comment_body += f"\n```diff\n{utils.MAX_CHAR_COUNT_REACHED}\n```"

    utils.debug_print(
        f"Repo={utils.REPO_NAME} pr_num={utils.PR_NUM} comment_title={utils.COMMENT_TITLE}"
    )

    return full_comment_body


if __name__ == "__main__":
    (
        pylint_file_name_in,
        output_to_console_in,
        common_ancestor_in,
        feature_branch_in,
    ) = parse_input_vars()

    pylint_comment, pylint_issues_found = parse_pylint_json(
        pylint_file_name_in, output_to_console_in, common_ancestor_in, feature_branch_in
    )
    if not output_to_console_in:
        comment_body_in = prepare_comment_body(pylint_comment, pylint_issues_found)
        utils.create_or_edit_comment(comment_body_in)

    sys.exit(pylint_issues_found)
