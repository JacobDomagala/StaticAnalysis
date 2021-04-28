import argparse
from github import Github
import os

# Input variables from Github action
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')
PR_NUM = int(os.getenv('INPUT_PR_NUM'))
WORK_DIR = os.getenv('GITHUB_WORKSPACE')
REPO_NAME = os.getenv('INPUT_REPO')
SHA = os.getenv('GITHUB_SHA')
COMMENT_TITLE = os.getenv('INPUT_COMMENT_TITLE')
ONLY_PR_CHANGES = os.getenv('INPUT_REPORD_PR_CHANGES_ONLY')

# Max characters per comment - 65536
# Make some room for HTML tags and error message
MAX_CHAR_COUNT_REACHED = '!Maximum character count per GitHub comment has been reached! Not all warnings/errors has been parsed!'
COMMENT_MAX_SIZE = 65000
current_comment_length = 0

def is_part_of_pr_changes(file_path, file_line_start, file_line_end):
    return True

def check_for_char_limit(incoming_line):
    global current_comment_length
    return (current_comment_length + len(incoming_line)) <= COMMENT_MAX_SIZE

def create_comment_for_output(tool_output, prefix):
    issues_found = 0
    global current_comment_length
    output_string = ''
    for line in tool_output:
        if line.startswith(prefix):
            issues_found += 1
            line = line.replace(prefix, "")
            file_path_end_idx = line.index(':')
            file_path = line[:file_path_end_idx]
            line = line[file_path_end_idx+1:]
            file_line_start = int(line[:line.index(':')])
            file_line_end = file_line_start + 5
            description = f"\n```diff\n!Line: {file_line_start} - {line[line.index(' ')+1:]}``` \n"

            new_line = f'\n\nhttps://github.com/{REPO_NAME}/blob/{SHA}/{file_path}#L{file_line_start}-L{file_line_end} {description} <br>\n'

            if is_part_of_pr_changes(file_path, file_line_start, file_line_end):
                if check_for_char_limit(new_line):
                    output_string += new_line
                    current_comment_length += len(new_line)
                else:
                    current_comment_length = COMMENT_MAX_SIZE
                    return output_string, issues_found

    return output_string, issues_found

def read_files_and_parse_results():
    # Get cppcheck and clang-tidy files
    parser = argparse.ArgumentParser()
    parser.add_argument('-cc', '--cppcheck', help='Output file name for cppcheck', required=True)
    parser.add_argument('-ct', '--clangtidy', help='Output file name for clang-tidy', required=True)
    cppcheck_file_name = parser.parse_args().cppcheck
    clangtidy_file_name = parser.parse_args().clangtidy

    cppcheck_content = ''
    with open(cppcheck_file_name, 'r') as file:
        cppcheck_content = file.readlines()

    clang_tidy_content = ''
    with open(clangtidy_file_name, 'r') as file:
        clang_tidy_content = file.readlines()

    line_prefix = f'{WORK_DIR}'

    cppcheck_comment, cppcheck_issues_found = create_comment_for_output(cppcheck_content, line_prefix)
    clang_tidy_comment, clang_tidy_issues_found = create_comment_for_output(clang_tidy_content, line_prefix)

    return cppcheck_comment, clang_tidy_comment, cppcheck_issues_found, clang_tidy_issues_found

def preapre_comment_body(cppcheck_comment, clang_tidy_comment, cppcheck_issues_found, clang_tidy_issues_found):
    full_comment_body = f'## <p align="center"><b> :zap: {COMMENT_TITLE} :zap: </b></p> \n\n'

    if cppcheck_issues_found > 0 or clang_tidy_issues_found > 0:
        if len(cppcheck_comment) > 0:
            full_comment_body +=f'<details> <summary> <b> :red_circle: Cppcheck found'\
            f' {cppcheck_issues_found} {"issues" if cppcheck_issues_found > 1 else "issue"}! Click here to see details. </b> </summary> <br>'\
            f'{cppcheck_comment} </details>'

        full_comment_body += "\n\n *** \n"

        if len(clang_tidy_comment) > 0:
            full_comment_body += f'<details> <summary> <b> :red_circle: clang-tidy found'\
            f' {clang_tidy_issues_found} {"issues" if cppcheck_issues_found > 1 else "issue"}! Click here to see details. </b> </summary> <br>'\
            f'{clang_tidy_comment} </details><br>\n'
    else:
        full_comment_body += f'\n\n## <p align="center"><b> :white_check_mark: No issues found! </b></p>'

    if current_comment_length == COMMENT_MAX_SIZE:
        full_comment_body += f'\n```diff\n{MAX_CHAR_COUNT_REACHED}\n```'

    print(f'Repo={REPO_NAME} pr_num={PR_NUM} comment_title={COMMENT_TITLE}')

    return full_comment_body

def create_or_edit_comment(comment_body):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUM)

    comments = pr.get_issue_comments()
    found_id = -1
    comment_to_edit = None
    for comment in comments:
        if (comment.user.login == 'github-actions[bot]') and (COMMENT_TITLE in comment.body):
            found_id = comment.id
            comment_to_edit = comment
            break

    if found_id != -1:
        comment_to_edit.edit(body = comment_body)
    else:
        pr.create_issue_comment(body = comment_body)


if __name__ == "__main__":
    cppcheck_comment, clang_tidy_comment, cppcheck_issues_found, clang_tidy_issues_found = read_files_and_parse_results()
    comment_body = preapre_comment_body(cppcheck_comment, clang_tidy_comment, cppcheck_issues_found, clang_tidy_issues_found)
    create_or_edit_comment(comment_body)
