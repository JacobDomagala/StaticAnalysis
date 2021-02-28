import argparse
from github import Github
import os

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

WORK_DIR = os.getenv('GITHUB_WORKSPACE')
REPO_NAME = os.getenv('INPUT_REPO')
SHA = os.getenv('GITHUB_SHA')
COMMENT_TITLE = os.getenv('INPUT_COMMENT_TITLE')

cppcheck_prefix = f'{WORK_DIR}'
clang_tidy_prefix = f'{WORK_DIR}'

cppcheck_comment = ''
for line in cppcheck_content:
    print(f'Parsing Line: \n {line}')
    print(f'With prefix={cppcheck_prefix}')
    if line.startswith(cppcheck_prefix):
        line = line.replace(cppcheck_prefix, "")
        file_path_end_idx = line.index(':')
        file_path = line[:file_path_end_idx]

        line = line[file_path_end_idx+1:]
        file_line_start = int(line[:line.index(':')])

        file_line_end = file_line_start + 5
        description = f"```diff !Line: {file_line_start} - {line[line.index(' ')+1:]} ```"
        cppcheck_comment += f'\nhttps://github.com/{REPO_NAME}/blob/{SHA}/{file_path}#L{file_line_start}-L{file_line_end} {description} </br>\n'

full_comment_body = f'<b>{COMMENT_TITLE} </b> </br>'\
    f'<details> <summary> <b>CPPCHECK</b> </summary> </br>'\
    f'{cppcheck_comment} </br>'

# Input variables from Github action
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')

PR_NUM = int(os.getenv('INPUT_PR_NUM'))



print(f'Repo={REPO_NAME} pr_num={PR_NUM} comment_title={COMMENT_TITLE}')

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUM)

comments = pr.get_issue_comments()
found_id = -1
comment_to_edit = None
for comment in comments:
    #print(f'Comment with ID={comment.id} user={comment.user} name={comment.user.login} body={comment.body}')
    if (comment.user.login == 'github-actions[bot]') and (COMMENT_TITLE in comment.body):
        print(f'Found Comment! with ID={comment.id} body={comment.body}')
        found_id = comment.id
        comment_to_edit = comment
        break

if found_id != -1:
    print(f'Editing existing comment!')
    comment_to_edit.edit(body = full_comment_body)
else:
    print(f'Adding new comment!')
    pr.create_issue_comment(body = full_comment_body)

