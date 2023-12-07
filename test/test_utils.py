import unittest
import os
import sys

try:
    project_path = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(project_path)
except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

from src import sa_utils


class TestUtils(unittest.TestCase):
    """Unit tests for utils_sa module"""

    maxDiff = None

    def test_get_lines_changed_from_patch(self):
        patch = "@@ -43,6 +48,8 @@\n@@ -0,0 +1 @@"

        lines = sa_utils.get_lines_changed_from_patch(patch)
        self.assertEqual(lines, [(48, 56), (1, 1)])


if __name__ == "__main__":
    unittest.main()
