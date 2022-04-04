# entrypoint to run StaticAnalysis Action

import os
import os.path
import stat
import subprocess
import sys
from github import Github


APT_PCKGS = os.getenv("INPUT_APT_PCKGS")
CLANG_TIDY_ARGS = os.getenv("INPUT_CLANG_TIDY_ARGS", "").split()
CMAKE_ARGS = os.getenv("INPUT_CMAKE_ARGS", "").split()
CPPCHECK_ARGS = os.getenv("INPUT_CPPCHECK_ARGS", "").split()
EXCLUDE_DIR = os.getenv("INPUT_EXCLUDE_DIR")
GITHUB_EVENT_NAME = os.getenv("GITHUB_EVENT_NAME")
GITHUB_TOKEN = os.getenv("INPUT_GITHUB_TOKEN")
INIT_SCRIPT = os.getenv("INPUT_INIT_SCRIPT")
PR_HEAD = os.getenv("INPUT_PR_HEAD")
PR_NUM = os.getenv("INPUT_PR_NUM")
PR_REPO = os.getenv("INPUT_PR_REPO")
PRINT_TO_CONSOLE = os.getenv("INPUT_FORCE_CONSOLE_PRINT", "false").lower() == "true"
TARGET_REPO_NAME = os.getenv("INPUT_REPO")
VERBOSE = os.getenv("INPUT_VERBOSE", "false").lower() == "true"


def debug_print(lines):
    if VERBOSE:
        print("\u001b[32m " + lines)


if PRINT_TO_CONSOLE:
    print("The 'force_console_print' option is enabled. Printing output to console.")
elif PR_HEAD == "":
    print("Pull request number input (pr_num) is not present. Printing output to console.")
    PRINT_TO_CONSOLE = True
else:
    print(f"Pull request number: {PR_NUM}")

if APT_PCKGS is not None:
    subprocess.run(["apt-get", "update"])
    subprocess.run(["apt-get", "install", "-y", APT_PCKGS])

debug_print(f"Repo = {PR_REPO}  PR_HEAD = {PR_HEAD} event name = {GITHUB_EVENT_NAME}")

USE_EXTRA_DIRECTORY = False

# This is useful when running this Action from fork (together with [pull_request_target])
if (GITHUB_EVENT_NAME == "pull_request_target") and (PR_REPO is not None):
    USE_EXTRA_DIRECTORY = True
    debug_print("Running in [pull_request_target] event! Cloning the Head repo ...")
    subprocess.run(["git", "clone", f"https://www.github.com/{PR_REPO}", "pr_tree"])
    os.chdir("pr_tree")
    subprocess.run(["git", "checkout", PR_HEAD])

    github = Github(GITHUB_TOKEN)
    os.environ["GITHUB_SHA"] = github.get_repo(TARGET_REPO_NAME).get_branch(PR_HEAD).commit.sha
    os.environ["GITHUB_WORKSPACE"] = os.path.realpath(os.path.curdir)

CURDIR = os.path.realpath(os.path.curdir)

if INIT_SCRIPT is not None:
    os.chmod(INIT_SCRIPT, stat.S_IRUSR | stat.S_IXUSR)
    subprocess.run(INIT_SCRIPT)

try:
    os.mkdir("build")
except FileExistsError:
    pass  # ignore 'File exists'

os.chdir("build")

cmake_command = ["cmake", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"]
cmake_command.extend(CMAKE_ARGS)
cmake_command.append("..")
debug_print(f"Running {' '.join(cmake_command)}")
p = subprocess.run(cmake_command)

get_files_command = ["python3", "get_files_to_check.py", f"-dir={CURDIR}"]
if EXCLUDE_DIR is not None:
    get_files_command.append(f"-exclude={CURDIR}/{EXCLUDE_DIR}")
debug_print(f"Running {' '.join(get_files_command)}")
p = subprocess.run(get_files_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
file_list = p.stdout.decode()

debug_print(f"Files to check = {file_list}")
debug_print(f"CPPCHECK_ARGS = {CPPCHECK_ARGS}")
debug_print(f"CLANG_TIDY_ARGS = {CLANG_TIDY_ARGS}")

# Build a command line for cppcheck.
cppcheck_command = ["cppcheck", "--project=compile_commands.json", "--output-file=cppcheck.txt"]
cppcheck_command.extend(CPPCHECK_ARGS)
if EXCLUDE_DIR is not None:
    cppcheck_command.append(f"-i{CURDIR}/{EXCLUDE_DIR}")

debug_print(f"Running {' '.join(cppcheck_command)}")
subprocess.run(cppcheck_command)

# Excludes for clang-tidy are handled in python script
clang_tidy_command = ["clang-tidy", f"-p={CURDIR}"]
clang_tidy_command.extend(CLANG_TIDY_ARGS)
clang_tidy_command.extend(file_list)

debug_print(f"Running {' '.join(clang_tidy_command)}")
p = subprocess.run(clang_tidy_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

with open("clang_tidy.txt", "w") as f:
    f.write(p.stdout.decode())

debug_print(f"Written to clang_tidy.txt: {p.stdout.decode()}")

p = subprocess.run(["python3", "/run_static_analysis.py",
                    "-cc", "cppcheck.txt", "-ct", "clang_tidy.txt",
                    "-o", str(PRINT_TO_CONSOLE).lower(),
                    "-fk", str(USE_EXTRA_DIRECTORY).lower()],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

sys.exit(p.returncode)
