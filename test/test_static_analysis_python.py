import json
import unittest
import os
import sys

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

from src import static_analysis_python


class TestStaticAnalysisPython(unittest.TestCase):
    """Unit tests for static_analysis_python"""

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

        pylint_content = r""" [
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 5,
            "column": 0,
            "endLine": 5,
            "endColumn": 5,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"shift\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 8,
            "column": 0,
            "endLine": 8,
            "endColumn": 7,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"letters\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 9,
            "column": 0,
            "endLine": 9,
            "endColumn": 7,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"encoded\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 13,
            "column": 12,
            "endLine": 13,
            "endColumn": 19,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"encoded\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 15,
            "column": 12,
            "endLine": 15,
            "endColumn": 13,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"x\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 16,
            "column": 12,
            "endLine": 16,
            "endColumn": 19,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"encoded\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 20,
            "column": 12,
            "endLine": 20,
            "endColumn": 19,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"encoded\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 22,
            "column": 12,
            "endLine": 22,
            "endColumn": 13,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"x\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        },
        {
            "type": "convention",
            "module": "dummy",
            "obj": "",
            "line": 23,
            "column": 12,
            "endLine": 23,
            "endColumn": 19,
            "path": "dummy.py",
            "symbol": "invalid-name",
            "message": "Constant name \"encoded\" doesn't conform to UPPER_CASE naming style",
            "message-id": "C0103"
        }
        ]"""

        files_changed_in_pr = {"/github/workspace/dummy.py": ("added", (1, 25))}
        result = static_analysis_python.create_comment_for_output(
            json.loads(pylint_content), files_changed_in_pr, False
        )

        sha = os.getenv("GITHUB_SHA")
        repo_name = os.getenv("INPUT_REPO")
        expected = (
            f"\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L5-L10 \n"
            "```diff"
            '\n!Line: 5 - C0103: Constant name "shift" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L8-L13 \n"
            "```diff\n"
            '!Line: 8 - C0103: Constant name "letters" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L9-L14 \n"
            "```diff\n"
            '!Line: 9 - C0103: Constant name "encoded" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "```"
            " \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L13-L18 \n"
            "```diff\n"
            '!Line: 13 - C0103: Constant name "encoded" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L15-L20 \n"
            "```diff\n"
            '!Line: 15 - C0103: Constant name "x" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L16-L21 \n"
            "```diff\n"
            '!Line: 16 - C0103: Constant name "encoded" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L20-L25 \n"
            "```diff\n"
            '!Line: 20 - C0103: Constant name "encoded" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L22-L25 \n"
            "```diff\n"
            '!Line: 22 - C0103: Constant name "x" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>"
            f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/dummy.py#L23-L25 \n"
            "```diff\n"
            '!Line: 23 - C0103: Constant name "encoded" doesn\'t conform to UPPER_CASE naming style (invalid-name)\n'
            "``` \n <br>\n"
        )

        print(result)

        self.assertEqual(result, (expected, 9))


if __name__ == "__main__":
    unittest.main()
