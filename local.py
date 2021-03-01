

cppcheck_file_name = 'cppcheck.txt'
clangtidy_file_name = 'clang-tidy.txt'

cppcheck_content = ''
with open(cppcheck_file_name, 'r') as file:
    cppcheck_content = file.readlines()

clang_tidy_content = ''
with open(clangtidy_file_name, 'r') as file:
    clang_tidy_content = file.readlines()

cppcheck_prefix = '/github/workspace'
cppcheck_comment = ''
REPO_NAME = "Repo/name/"
SHA = "08027850251-4394-10939fg"

def test(val):
    val += 10

val = 20
test(val)

print(f"Final result: {val}")

