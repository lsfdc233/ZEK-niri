import unittest
from unittest.mock import patch

from tests.utils import TempEnv
from zekniri.state.backup import (
    backup_configs,
    get_all_backups,
    list_backups,
    rollback_configs,
    delete_backup,
)


class BackupTest(unittest.TestCase):
    def _deploy_example(self, t):
        from zekniri.deploy.deploy import deploy_selected_configs
        src = t.home / "configs" / "app"
        src.mkdir(parents=True)
        (src / "conf").write_text("v1", encoding="utf-8")
        deploy_selected_configs(items_to_deploy=["app"])

    def test_snapshot_and_list(self):
        with TempEnv() as t:
            self._deploy_example(t)
            snap = backup_configs(note="first", interactive=False)
            self.assertIsNotNone(snap)
            self.assertTrue((snap / "app" / "conf").is_file())
            self.assertEqual((snap / "note.txt").read_text(encoding="utf-8"), "first")
            self.assertEqual(len(get_all_backups()), 1)
            list_backups()

    def test_rollback_restores_previous_content(self):
        with TempEnv() as t:
            self._deploy_example(t)
            backup_configs(interactive=False)
            # Change deployed content, then roll back.
            (t.home / ".config" / "app" / "conf").write_text("v2", encoding="utf-8")
            self.assertTrue(rollback_configs(""))
            self.assertEqual((t.home / ".config" / "app" / "conf").read_text(encoding="utf-8"), "v1")

    def test_delete_snapshot(self):
        with TempEnv() as t:
            self._deploy_example(t)
            snap = backup_configs(interactive=False)
            self.assertTrue(delete_backup(snap.name))
            self.assertEqual(get_all_backups(), [])

    def test_prune_keeps_max(self):
        with TempEnv() as t:
            with patch("zekniri.state.backup.MAX_SNAPSHOTS", 2):
                self._deploy_example(t)
                for _ in range(3):
                    backup_configs(interactive=False)
            self.assertEqual(len(get_all_backups()), 2)


if __name__ == "__main__":
    unittest.main()
