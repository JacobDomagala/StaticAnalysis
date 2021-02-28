

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


print(f"Final result: {cppcheck_comment}")

