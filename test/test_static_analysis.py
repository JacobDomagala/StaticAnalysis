import unittest
import os
import sys

try:
    project_path = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(project_path)
except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

os.environ["GITHUB_WORKSPACE"] = f"{project_path}/test/utils"
os.environ["INPUT_VERBOSE"] = "True"
os.environ["INPUT_REPORT_PR_CHANGES_ONLY"] = "False"
os.environ["INPUT_REPO"] = "RepoName"
os.environ["GITHUB_SHA"] = "1234"

from src import run_static_analysis, get_files_to_check


def to_list_and_sort(string_in):
    # create list (of strings) from space separated string
    # and then sort it
    list_out = string_in.split(" ")
    list_out.sort()

    return list_out


class TestRunStaticAnalysis(unittest.TestCase):
    """Unit tests for run_static_analysis module"""

    def test_create_comment_for_output(self):

        cppcheck_content = [
            "/github/workspace/DummyFile.cpp:8:23: style: Error message\n",
            "    Part of code\n",
            "               ^\n",
            "/github/workspace/DummyFile.cpp:6:12: note: Note message\n",
            "    Part of code\n",
            "               ^\n",
            "/github/workspace/DummyFile.cpp:7:4: note: Another note message\n",
            "    Part of code\n",
            "               ^\n",
            "/github/workspace/DummyFile.cpp:3:0: style: Error message\n",
            "    Part of code\n",
            "               ^\n",
        ]

        files_changed_in_pr = {
            "/github/workspace/DummyFile.hpp": ("added", (1, 10)),
            "/github/workspace/DummyFile.cpp": ("added", (1, 10)),
        }
        result = run_static_analysis.create_comment_for_output(
            cppcheck_content, "/github/workspace", files_changed_in_pr, False
        )

        sha = os.getenv("GITHUB_SHA")
        repo_name = os.getenv("INPUT_REPO")
        expected = (
            f"\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L8-L9 \n"
            f"```diff\n!Line: 8 - style: Error message"
            f"\n!Line: 6 - note: Note message"
            f"\n!Line: 7 - note: Another note message\n``` "
            f"\n\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L3-L8 \n"
            f"```diff\n!Line: 3 - style: Error message\n``` \n <br>\n"
        )

        print(result)

        self.assertEqual(result, (expected, 2))

    def test_prepare_comment_body(self):
        sha = os.getenv("GITHUB_SHA")
        repo_name = os.getenv("INPUT_REPO")

        clang_tidy_comment = (
            f"\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L8-L9 \n"
            f"```diff\n!Line: 8 - style: Error message"
            f"\n!Line: 6 - note: Note message"
            f"\n!Line: 7 - note: Another note message\n``` "
            f"\n\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L3-L8 \n"
            f"```diff\n!Line: 3 - style: Error message\n``` \n <br>\n"
        )

        COMMENT_TITLE = os.getenv("INPUT_COMMENT_TITLE")
        comment_body = run_static_analysis.prepare_comment_body("", "", 0, 0)

        expected_comment_body = (
            '## <p align="center"><b> :white_check_mark:'
            f"{COMMENT_TITLE} - no issues found! :white_check_mark: </b></p>"
        )

        self.assertEqual(expected_comment_body, comment_body)

    def test_get_files_to_check(self):
        pwd = os.path.dirname(os.path.realpath(__file__))

        # Excludes == None
        expected = [
            f"{pwd}/utils/DummyFile.cpp",
            f"{pwd}/utils/DummyFile.hpp",
            f"{pwd}/utils/exclude_dir_1/ExcludedFile1.hpp",
            f"{pwd}/utils/exclude_dir_2/ExcludedFile2.hpp",
        ]
        result = get_files_to_check.get_files_to_check(f"{pwd}/utils", None)

        self.assertEqual(to_list_and_sort(result), expected)

        # Single exclude_dir
        expected = [
            f"{pwd}/utils/DummyFile.cpp",
            f"{pwd}/utils/DummyFile.hpp",
            f"{pwd}/utils/exclude_dir_2/ExcludedFile2.hpp",
        ]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils", f"{pwd}/utils/exclude_dir_1"
        )

        self.assertEqual(to_list_and_sort(result), expected)

        # Multiple exclude_dir
        expected = [f"{pwd}/utils/DummyFile.cpp", f"{pwd}/utils/DummyFile.hpp"]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils", f"{pwd}/exclude_dir_1 {pwd}/exclude_dir_2"
        )


if __name__ == "__main__":
    unittest.main()
