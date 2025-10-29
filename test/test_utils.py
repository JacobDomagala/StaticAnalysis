import unittest
import os
import sys
import json
import tempfile

try:
    PROJECT_PATH = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(PROJECT_PATH)
except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

from src import patch_compile_commands, sa_utils


class TestUtils(unittest.TestCase):
    """Unit tests for utils_sa module"""

    maxDiff = None

    def test_get_lines_changed_from_patch(self):
        patch = "@@ -43,6 +48,8 @@\n@@ -0,0 +1 @@"

        lines = sa_utils.get_lines_changed_from_patch(patch)
        self.assertEqual(lines, [(48, 56), (1, 1)])

    def test_is_excluded_dir_with_multiple_directories(self):
        previous_exclude_dir = os.environ.get("INPUT_EXCLUDE_DIR")
        previous_work_dir = sa_utils.WORK_DIR

        try:
            os.environ["INPUT_EXCLUDE_DIR"] = "exclude_dir_1 exclude_dir_2"
            sa_utils.WORK_DIR = "/github/workspace"

            self.assertTrue(
                sa_utils.is_excluded_dir(
                    "/github/workspace/exclude_dir_1/file.cpp:8:1: warning"
                )
            )
            self.assertTrue(
                sa_utils.is_excluded_dir(
                    "/github/workspace/exclude_dir_2/file.cpp:3:1: warning"
                )
            )
            self.assertFalse(
                sa_utils.is_excluded_dir("/github/workspace/src/file.cpp:4:1: warning")
            )
        finally:
            if previous_exclude_dir is None:
                os.environ.pop("INPUT_EXCLUDE_DIR", None)
            else:
                os.environ["INPUT_EXCLUDE_DIR"] = previous_exclude_dir
            sa_utils.WORK_DIR = previous_work_dir

    def test_patch_compile_commands_uses_current_workspace(self):
        previous_workspace = os.environ.get("GITHUB_WORKSPACE")

        try:
            os.environ["GITHUB_WORKSPACE"] = "/github/workspace/pr_tree"
            with tempfile.NamedTemporaryFile("w+", encoding="utf-8") as compile_db:
                json.dump(
                    [
                        {
                            "directory": "/src/build",
                            "command": "clang++ -I/src/include -c /src/source.cpp",
                            "file": "/src/source.cpp",
                        }
                    ],
                    compile_db,
                )
                compile_db.flush()

                patch_compile_commands.patch_compile_commands(compile_db.name)
                compile_db.seek(0)
                patched = json.load(compile_db)

            self.assertEqual(patched[0]["directory"], "/github/workspace/pr_tree/build")
            self.assertEqual(patched[0]["file"], "/github/workspace/pr_tree/source.cpp")
            self.assertEqual(
                patched[0]["command"],
                "clang++ -I/github/workspace/pr_tree/include "
                "-c /github/workspace/pr_tree/source.cpp",
            )
        finally:
            if previous_workspace is None:
                os.environ.pop("GITHUB_WORKSPACE", None)
            else:
                os.environ["GITHUB_WORKSPACE"] = previous_workspace


if __name__ == "__main__":
    unittest.main()
