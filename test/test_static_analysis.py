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

from src import run_static_analysis


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


if __name__ == "__main__":
    unittest.main()
