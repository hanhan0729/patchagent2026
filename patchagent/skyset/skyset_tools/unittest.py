from collections import namedtuple
from typing import Generator

import os
import unittest
import skyset_tools

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
PatchTask = namedtuple("PatchTask", ["project", "tag", "sanitizer"])


def make_task(project: str, tag: str) -> PatchTask:
    return PatchTask(project, tag, skyset_tools.get_config(project, tag)["sanitizer"])


def get_all_task() -> Generator[PatchTask, None, None]:
    for project in os.listdir(ROOT):
        if (
            os.path.isdir(project_path := os.path.join(ROOT, project))
            and project not in ["skyset_tools", ".git"]
            and not project.startswith("external-")
        ):
            for tag in os.listdir(project_path):
                if os.path.isdir(os.path.join(project_path, tag)):
                    yield make_task(project, tag)


class TestBuildAndTest(unittest.TestCase):
    def test_build_test_without_debug(self):
        """Test the build and test process over all tasks without debug information."""
        for task in get_all_task():
            print(f"Buiding and testing {task}...")
            ret, _ = skyset_tools.build(task.project, task.tag, task.sanitizer)
            self.assertTrue(ret, "Build should return True.")

            print(f"Testing {task}...")
            ret, report = skyset_tools.test(task.project, task.tag, task.sanitizer)
            self.assertTrue(ret, "Test should return True.")
            self.assertTrue(len(report) > 0, "Test report should not be empty.")

    def do_test(self, task):
        try:
            print(f"Testing {task}...")
            ret, report = skyset_tools.test(task.project, task.tag, task.sanitizer)
            assert ret, "Test should return True."
            assert len(report) > 0, "Test report should not be empty."

            with open(skyset_tools.get_report_path(task.project, task.tag), "w") as f:
                f.write(report)
        except Exception:
            return False
        return True

    def test_build_test_with_debug(self):
        fail_cases = []
        for task in get_all_task():
            if not self.do_test(task):
                print("Rebuilding and retesting...")
                ret, _ = skyset_tools.build(task.project, task.tag, task.sanitizer)
                if not ret or not self.do_test(task):
                    fail_cases.append(task)
                    print(f"Failed task: {task}")

        self.assertEqual(len(fail_cases), 0, f"{len(fail_cases)} failed cases.")


if __name__ == "__main__":
    unittest.main(verbosity=2)

# python3 -m unittest -v skyset_tools.unittest.TestBuildAndTest.test_build_test_without_debug
# python3 -m unittest -v skyset_tools.unittest.TestBuildAndTest.test_build_test_with_debug
