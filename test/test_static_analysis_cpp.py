import unittest
import os
import sys
import utils.helper_functions as utils

try:
    project_path = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(project_path)
except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

os.environ["GITHUB_WORKSPACE"] = f"{project_path}/test/utils/dummy_project"
os.environ["INPUT_VERBOSE"] = "True"
os.environ["INPUT_REPORT_PR_CHANGES_ONLY"] = "False"
os.environ["INPUT_REPO"] = "RepoName"
os.environ["GITHUB_SHA"] = "1234"
os.environ["INPUT_COMMENT_TITLE"] = "title"

from src import static_analysis_cpp, get_files_to_check


def to_list_and_sort(string_in):
    # create list (of strings) from space separated string
    # and then sort it
    list_out = string_in.split(" ")
    list_out.sort()

    return list_out


class TestStaticAnalysisCpp(unittest.TestCase):
    """Unit tests for static_analysis_cpp"""

    maxDiff = None

    def test_create_comment_for_output(self):
        """
        Test the `create_comment_for_output()` function.

        This test case checks whether the `create_comment_for_output()` function correctly
        generates a GitHub comment that displays static analysis issues for a given set of
        files.

        The test case creates a mock set of files and static analysis issues, and expects the
        generated GitHub comment to match a pre-defined expected string.
        """

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
        result = static_analysis_cpp.create_comment_for_output(
            cppcheck_content, "/github/workspace", files_changed_in_pr, False
        )

        sha = os.getenv("GITHUB_SHA")
        repo_name = os.getenv("INPUT_REPO")
        expected = (
            f"\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L8-L9 \n"
            f"```diff\n!Line: 8 - style: Error message"
            f"\n\n!Line: 6 - note: Note message"
            f"\n!Line: 7 - note: Another note message\n``` "
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L3-L8 \n"
            f"```diff\n!Line: 3 - style: Error message\n\n``` \n <br>\n"
        )

        print(result)

        self.assertEqual(result, (expected, 2))

    def test_prepare_comment_body(self):
        """
        Test the `prepare_comment_body()` function.

        This test case checks whether the `prepare_comment_body()` function correctly generates
        the body text of a GitHub comment for a given set of static analysis issues.

        The test case creates mock input parameters representing different types of static
        analysis issues, and expects the generated comment body to match a pre-defined expected
        string.
        """

        comment_title = os.getenv("INPUT_COMMENT_TITLE")
        comment_body = static_analysis_cpp.prepare_comment_body("", "", 0, 0)

        # Empty results
        expected_comment_body = utils.generate_comment(comment_title, "", 0, "cppcheck")

        self.assertEqual(expected_comment_body, comment_body)

        # Multiple cppcheck issues
        cppcheck_issues_found = 4
        cppcheck_comment = "dummy issues"
        expected_comment_body = utils.generate_comment(
            comment_title, cppcheck_comment, cppcheck_issues_found, "cppcheck"
        )

        comment_body = static_analysis_cpp.prepare_comment_body(
            cppcheck_comment, "", cppcheck_issues_found, 0
        )

        self.assertEqual(expected_comment_body, comment_body)

        # Single cppcheck issue
        cppcheck_issues_found = 1
        cppcheck_comment = "dummy issue"
        expected_comment_body = utils.generate_comment(
            comment_title, cppcheck_comment, cppcheck_issues_found, "cppcheck"
        )

        comment_body = static_analysis_cpp.prepare_comment_body(
            cppcheck_comment, "", cppcheck_issues_found, 0
        )

        self.assertEqual(expected_comment_body, comment_body)

        # Multiple clang-tidy issues
        clang_tidy_issues_found = 4
        clang_tidy_comment = "dummy issues"
        expected_comment_body = utils.generate_comment(
            comment_title, clang_tidy_comment, clang_tidy_issues_found, "clang-tidy"
        )

        comment_body = static_analysis_cpp.prepare_comment_body(
            "", clang_tidy_comment, 0, clang_tidy_issues_found
        )

        self.assertEqual(expected_comment_body, comment_body)

        # Single clang-tidy issue
        clang_tidy_issues_found = 1
        clang_tidy_comment = "dummy issue"
        expected_comment_body = utils.generate_comment(
            comment_title, clang_tidy_comment, clang_tidy_issues_found, "clang-tidy"
        )

        comment_body = static_analysis_cpp.prepare_comment_body(
            "", clang_tidy_comment, 0, clang_tidy_issues_found
        )

        self.assertEqual(expected_comment_body, comment_body)

    def test_get_files_to_check(self):
        """
        Test the `get_files_to_check()` function.

        This test case checks whether the `get_files_to_check()` function correctly generates a
        list of file paths to check for static analysis issues in a given directory, excluding
        any directories that should be skipped.

        The test case creates a mock directory structure and a set of directories to skip,
        and expects the generated list of file paths to match a pre-defined expected list of
        file paths.
        """

        pwd = os.path.dirname(os.path.realpath(__file__))

        # Excludes == None
        expected = [
            f"{pwd}/utils/dummy_project/DummyFile.cpp",
            f"{pwd}/utils/dummy_project/DummyFile.hpp",
            f"{pwd}/utils/dummy_project/exclude_dir_1/ExcludedFile1.hpp",
            f"{pwd}/utils/dummy_project/exclude_dir_2/ExcludedFile2.hpp",
        ]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils/dummy_project", None, "", "c++"
        )

        self.assertEqual(to_list_and_sort(result), expected)

        # Single exclude_dir
        expected = [
            f"{pwd}/utils/dummy_project/DummyFile.cpp",
            f"{pwd}/utils/dummy_project/DummyFile.hpp",
            f"{pwd}/utils/dummy_project/exclude_dir_2/ExcludedFile2.hpp",
        ]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils/dummy_project",
            f"{pwd}/utils/dummy_project/exclude_dir_1",
            "",
            "c++",
        )

        self.assertEqual(to_list_and_sort(result), expected)

        # Multiple exclude_dir
        expected = [
            f"{pwd}/utils/dummy_project/DummyFile.cpp",
            f"{pwd}/utils/dummy_project/DummyFile.hpp",
        ]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils/dummy_project",
            f"{pwd}/utils/dummy_project/exclude_dir_1 {pwd}/utils/dummy_project/exclude_dir_2",
            "",
            "c++",
        )

        # Preselected files present
        expected = [f"{pwd}/utils/dummy_project/DummyFile.cpp"]
        result = get_files_to_check.get_files_to_check(
            f"{pwd}/utils/dummy_project",
            f"{pwd}/utils/dummy_project/exclude_dir_1 {pwd}/utils/dummy_project/exclude_dir_2",
            f"{pwd}/utils/dummy_project/DummyFile.cpp {pwd}/utils/dummy_project/exclude_dir_1/ExcludedFile1.hpp",
            "c++",
        )


if __name__ == "__main__":
    unittest.main()
