import argparse
import os
import sys
from github import Github

# Input variables from Github action
GITHUB_TOKEN = os.getenv("INPUT_GITHUB_TOKEN")
PR_NUM = os.getenv("INPUT_PR_NUM")
WORK_DIR = os.getenv("GITHUB_WORKSPACE")
REPO_NAME = os.getenv("INPUT_REPO")
SHA = os.getenv("GITHUB_SHA")
COMMENT_TITLE = os.getenv("INPUT_COMMENT_TITLE")
ONLY_PR_CHANGES = os.getenv("INPUT_REPORT_PR_CHANGES_ONLY")
VERBOSE = os.getenv("INPUT_VERBOSE", "False").lower() in ("true", "True")

# Max characters per comment - 65536
# Make some room for HTML tags and error message
MAX_CHAR_COUNT_REACHED = (
    "!Maximum character count per GitHub comment has been reached!"
    " Not all warnings/errors has been parsed!"
)
COMMENT_MAX_SIZE = 65000
CURRENT_COMMENT_LENGTH = 0


def is_part_of_pr_changes(file_path, issue_file_line, files_changed_in_pr):
    if ONLY_PR_CHANGES == "false":
        return True

    file_name = file_path[file_path.rfind("/") + 1 :]
    print(f"Looking for issue found in file={file_name} ...")
    for file, (status, lines_changed_for_file) in files_changed_in_pr.items():
        print(
            f"Changed file by this PR {file} with status {status} and changed lines {lines_changed_for_file}"
        )
        if file == file_name:
            if status == "added":
                return True

            for (start, end) in lines_changed_for_file:
                if start <= issue_file_line <= end:
                    return True

    return False


def get_lines_changed_from_patch(patch):
    lines_changed = []
    lines = patch.split("\n")

    for line in lines:
        # Example line @@ -43,6 +48,8 @@
        # ------------ ^
        if line.startswith("@@"):
            # Example line @@ -43,6 +48,8 @@
            # ----------------------^
            idx_beg = line.index("+")

            # Example line @@ -43,6 +48,8 @@
            #                       ^--^
            try:
                idx_end = line[idx_beg:].index(",")
                line_begin = int(line[idx_beg + 1 : idx_beg + idx_end])

                idx_beg = idx_beg + idx_end
                idx_end = line[idx_beg + 1 :].index("@@")

                num_lines = int(line[idx_beg + 1 : idx_beg + idx_end])
            except ValueError:
                # Special case for single line files
                # such as @@ -0,0 +1 @@
                idx_end = line[idx_beg:].index(" ")
                line_begin = int(line[idx_beg + 1 : idx_beg + idx_end])
                num_lines = 0

            lines_changed.append((line_begin, line_begin + num_lines))

    return lines_changed


def setup_changed_files():
    files_changed = dict()

    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(REPO_NAME)
    pull_request = repo.get_pull(int(PR_NUM))
    num_changed_files = pull_request.changed_files
    print(f"Changed files {num_changed_files}")
    files = pull_request.get_files()
    for file in files:
        if file.patch is not None:
            lines_changed_for_file = get_lines_changed_from_patch(file.patch)
            files_changed[file.filename] = (file.status, lines_changed_for_file)

    return files_changed


def check_for_char_limit(incoming_line):
    global CURRENT_COMMENT_LENGTH
    return (CURRENT_COMMENT_LENGTH + len(incoming_line)) <= COMMENT_MAX_SIZE


def is_excluded_dir(line):
    # In future this could be multiple different directories
    exclude_dir = os.getenv("INPUT_EXCLUDE_DIR")
    if not exclude_dir:
        return False

    excluded_dir = f"{WORK_DIR}/{exclude_dir}"
    if VERBOSE:
        print(f"{line} and {excluded_dir} with result {line.startswith(excluded_dir)}")

    return line.startswith(excluded_dir)


def get_file_line_end(file, file_line_start):
    num_lines = sum(1 for line in open(WORK_DIR + file))
    return min(file_line_start + 5, num_lines)


def create_comment_for_output(
    tool_output, prefix, files_changed_in_pr, output_to_console
):
    issues_found = 0
    global CURRENT_COMMENT_LENGTH
    output_string = ""
    for line in tool_output:
        if line.startswith(prefix) and not is_excluded_dir(line):
            # In case where we only output to console, skip the next part
            if output_to_console:
                output_string += f"\n{line}"
                issues_found += 1
                continue

            line = line.replace(prefix, "")
            file_path_end_idx = line.index(":")
            file_path = line[:file_path_end_idx]
            line = line[file_path_end_idx + 1 :]
            file_line_start = int(line[: line.index(":")])
            file_line_end = get_file_line_end(file_path, file_line_start)
            description = f"\n```diff\n!Line: {file_line_start} - {line[line.index(' ')+1:]}``` \n"

            new_line = (
                f"\n\nhttps://github.com/{REPO_NAME}/blob/{SHA}{file_path}"
                f"#L{file_line_start}-L{file_line_end} {description} <br>\n"
            )

            if is_part_of_pr_changes(file_path, file_line_start, files_changed_in_pr):
                if check_for_char_limit(new_line):
                    output_string += new_line
                    CURRENT_COMMENT_LENGTH += len(new_line)
                    issues_found += 1
                else:
                    CURRENT_COMMENT_LENGTH = COMMENT_MAX_SIZE
                    return output_string, issues_found

    return output_string, issues_found


def read_files_and_parse_results():
    # Get cppcheck and clang-tidy files
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-cc", "--cppcheck", help="Output file name for cppcheck", required=True
    )
    parser.add_argument(
        "-ct", "--clangtidy", help="Output file name for clang-tidy", required=True
    )
    parser.add_argument(
        "-o",
        "--output_to_console",
        help="Whether to output the result to console",
        required=True,
    )
    cppcheck_file_name = parser.parse_args().cppcheck
    clangtidy_file_name = parser.parse_args().clangtidy
    output_to_console = parser.parse_args().output_to_console == "true"

    cppcheck_content = ""
    with open(cppcheck_file_name, "r") as file:
        cppcheck_content = file.readlines()

    clang_tidy_content = ""
    with open(clangtidy_file_name, "r") as file:
        clang_tidy_content = file.readlines()

    line_prefix = f"{WORK_DIR}"
    if VERBOSE:
        print(f"Cppcheck result: \n {cppcheck_content} \n")
        print(f"clang-tidy result: \n {clang_tidy_content} \n")
        print(f"line_prefix: {line_prefix} \n")

    files_changed_in_pr = dict()
    if not output_to_console:
        files_changed_in_pr = setup_changed_files()

    cppcheck_comment, cppcheck_issues_found = create_comment_for_output(
        cppcheck_content, line_prefix, files_changed_in_pr, output_to_console
    )
    clang_tidy_comment, clang_tidy_issues_found = create_comment_for_output(
        clang_tidy_content, line_prefix, files_changed_in_pr, output_to_console
    )

    if output_to_console and (cppcheck_issues_found or clang_tidy_issues_found):
        print("##[error] Issues found!\n")
        if cppcheck_issues_found:
            print(f"\u001b[31m cppcheck results: {cppcheck_comment}")

        if clang_tidy_issues_found:
            print(f"clang-tidy results: {clang_tidy_comment}")

    return (
        cppcheck_comment,
        clang_tidy_comment,
        cppcheck_issues_found,
        clang_tidy_issues_found,
        output_to_console,
    )


def prepare_comment_body(
    cppcheck_comment, clang_tidy_comment, cppcheck_issues_found, clang_tidy_issues_found
):

    if cppcheck_issues_found == 0 and clang_tidy_issues_found == 0:
        full_comment_body = (
            '## <p align="center"><b> :white_check_mark:'
            f"{COMMENT_TITLE} - no issues found! :white_check_mark: </b></p>"
        )
    else:
        full_comment_body = (
            f'## <p align="center"><b> :zap: {COMMENT_TITLE} :zap: </b></p> \n\n'
        )

        if len(cppcheck_comment) > 0:
            full_comment_body += (
                f"<details> <summary> <b> :red_circle: Cppcheck found "
                f"{cppcheck_issues_found} {'issues' if cppcheck_issues_found > 1 else 'issue'}!"
                " Click here to see details. </b> </summary> <br>"
                f"{cppcheck_comment} </details>"
            )

        full_comment_body += "\n\n *** \n"

        if len(clang_tidy_comment) > 0:
            full_comment_body += (
                f"<details> <summary> <b> :red_circle: clang-tidy found "
                f"{clang_tidy_issues_found} {'issues' if clang_tidy_issues_found > 1 else 'issue'}!"
                " Click here to see details. </b> </summary> <br>"
                f"{clang_tidy_comment} </details><br>\n"
            )

    if CURRENT_COMMENT_LENGTH == COMMENT_MAX_SIZE:
        full_comment_body += f"\n```diff\n{MAX_CHAR_COUNT_REACHED}\n```"

    print(f"Repo={REPO_NAME} pr_num={PR_NUM} comment_title={COMMENT_TITLE}")

    return full_comment_body


def create_or_edit_comment(comment_body):
    github = Github(GITHUB_TOKEN)
    repo = github.get_repo(REPO_NAME)
    pull_request = repo.get_pull(int(PR_NUM))

    comments = pull_request.get_issue_comments()
    found_id = -1
    comment_to_edit = None
    for comment in comments:
        if (comment.user.login == "github-actions[bot]") and (
            COMMENT_TITLE in comment.body
        ):
            found_id = comment.id
            comment_to_edit = comment
            break

    if found_id != -1:
        comment_to_edit.edit(body=comment_body)
    else:
        pull_request.create_issue_comment(body=comment_body)


if __name__ == "__main__":
    (
        cppcheck_comment_in,
        clang_tidy_comment_in,
        cppcheck_issues_found_in,
        clang_tidy_issues_found_in,
        output_to_console_in,
    ) = read_files_and_parse_results()

    if not output_to_console_in:
        comment_body_in = prepare_comment_body(
            cppcheck_comment_in,
            clang_tidy_comment_in,
            cppcheck_issues_found_in,
            clang_tidy_issues_found_in,
        )
        create_or_edit_comment(comment_body_in)

    sys.exit(cppcheck_issues_found_in + clang_tidy_issues_found_in)
