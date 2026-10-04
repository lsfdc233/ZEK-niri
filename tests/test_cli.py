import unittest

from tests.utils import TempEnv
from zekniri import cli


class CliTest(unittest.TestCase):
    def _make_app(self, t):
        app = t.home / "configs" / "kitty"
        app.mkdir(parents=True)
        (app / "conf").write_text("x", encoding="utf-8")

    def test_help_returns_zero(self):
        self.assertEqual(cli._cmd_help([]), 0)

    def test_list_snapshot_returns_zero(self):
        with TempEnv() as t:
            self.assertEqual(cli._cmd_list([]), 0)

    def test_help_rejects_args(self):
        with self.assertRaises(SystemExit) as cm:
            cli._cmd_help(["extra"])
        self.assertEqual(cm.exception.code, 2)

    def test_install_config_mode_deploys(self):
        with TempEnv() as t:
            self._make_app(t)
            self.assertEqual(cli._cmd_install(["config"]), 0)
            self.assertTrue((t.home / ".config" / "kitty" / "conf").is_file())

    def test_install_rejects_bad_mode(self):
        with self.assertRaises(SystemExit):
            cli._cmd_install(["nonsense"])

    def test_commands_dict_shape(self):
        for name, (handler, usage) in cli.COMMANDS.items():
            self.assertTrue(callable(handler), name)
            self.assertIsInstance(usage, str, name)


if __name__ == "__main__":
    unittest.main()
