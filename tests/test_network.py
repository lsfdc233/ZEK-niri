import unittest
from pathlib import Path

from tests.utils import TempEnv
from zekniri.network import _build_pull_cmd, safe_git_pull


class NetworkTest(unittest.TestCase):
    def test_pull_cmd_shape_quiet(self):
        cmd = _build_pull_cmd(Path("/tmp/repo"), quiet=True)
        self.assertEqual(cmd[0], "git")
        self.assertIn("-C", cmd)
        self.assertIn("/tmp/repo", cmd)
        self.assertIn("pull", cmd)
        self.assertIn("--ff-only", cmd)
        self.assertIn("--quiet", cmd)
        self.assertIn("http.connectTimeout=10", cmd)

    def test_pull_cmd_shape_loud_has_no_quiet(self):
        cmd = _build_pull_cmd(Path("/tmp/repo"), quiet=False)
        self.assertNotIn("--quiet", cmd)

    def test_safe_git_pull_system_mode_is_noop(self):
        with TempEnv() as t:
            t.env.run_mode = "system"
            self.assertIsNone(safe_git_pull(t.env.repo_dir))

    def test_safe_git_pull_non_git_returns_false(self):
        with TempEnv() as t:
            t.env.run_mode = "repo"
            self.assertFalse(safe_git_pull(t.home / "not-a-repo"))


if __name__ == "__main__":
    unittest.main()
