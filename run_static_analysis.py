import argparse
from github import Github
import os

# Get cppcheck and clang-tidy files
parser = argparse.ArgumentParser()
parser.add_argument('-cc', '--cppcheck', help='Output file name for cppcheck', required=True)
parser.add_argument('-ct', '--clangtidy', help='Output file name for clang-tidy', required=True)
cppcheck_file_name = parser.parse_args().cppcheck
clangtidy_file_name = parser.parse_args().clangtidy

# Input variables from Github action
GITHUB_TOKEN = os.getenv('INPUT_GITHUB_TOKEN')
REPO_NAME = os.getenv('INPUT_REPO')
PR_NUM = int(os.getenv('INPUT_PR_NUM'))
COMMENT_TITLE = os.getenv('INPUT_COMMENT_TITLE')

print(f'Repo={REPO_NAME} pr_num={PR_NUM} comment_title={COMMENT_TITLE}')

g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
pr = repo.get_pull(PR_NUM)

comments = pr.get_issue_comments()
found_id = -1
comment_to_edit = None
for comment in comments:
    print(f'Comment with ID={comment.id} user={comment.user} name={comment.user.login} body={comment.body}')
    if (comment.user.login == 'github-actions[bot]') and (COMMENT_TITLE in comment.body):
        print(f'Found Comment! with ID={comment.id} body={comment.body}')
        found_id = comment.id
        comment_to_edit = comment
        break

if found_id != -1:
    print(f'Editing existing comment!')
    comment_to_edit.edit(body = f"{COMMENT_TITLE} Body after edit")
else:
    print(f'Adding new comment!')
    pr.create_issue_comment(body = f"{COMMENT_TITLE} new body")

