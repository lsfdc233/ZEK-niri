import unittest

from tests.utils import TempEnv
from zekniri.state.uninstall import uninstall_zekniri


class UninstallTest(unittest.TestCase):
    def _deploy(self, t):
        from zekniri.deploy.deploy import deploy_selected_configs
        src = t.home / "configs" / "app"
        src.mkdir(parents=True)
        (src / "conf").write_text("x", encoding="utf-8")
        deploy_selected_configs(items_to_deploy=["app"])

    def test_keep_data_removes_config_only(self):
        with TempEnv() as t:
            self._deploy(t)
            (t.env.nyx_dir / "backups").mkdir(parents=True, exist_ok=True)
            (t.env.nyx_dir / "marker").write_text("keep", encoding="utf-8")
            self.assertTrue(uninstall_zekniri("keep-data"))
            self.assertFalse((t.home / ".config" / "app").exists())
            self.assertTrue((t.env.nyx_dir / "marker").is_file())

    def test_purge_removes_tool_data(self):
        with TempEnv() as t:
            self._deploy(t)
            (t.env.nyx_dir / "backups").mkdir(parents=True, exist_ok=True)
            t.env.state_dir.mkdir(parents=True, exist_ok=True)
            self.assertTrue(uninstall_zekniri("purge"))
            self.assertFalse((t.home / ".config" / "app").exists())
            self.assertFalse(t.env.nyx_dir.exists())

    def test_nothing_installed(self):
        with TempEnv() as t:
            (t.home / "configs").mkdir(exist_ok=True)
            self.assertTrue(uninstall_zekniri(""))


if __name__ == "__main__":
    unittest.main()
