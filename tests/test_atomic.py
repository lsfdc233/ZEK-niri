import unittest
from pathlib import Path
from unittest.mock import patch

from tests.utils import TempEnv
from zekniri.deploy.atomic import atomic_replace_item


class AtomicReplaceTest(unittest.TestCase):
    def _src(self, root: Path, name: str) -> Path:
        src = root / "src" / name
        src.mkdir(parents=True)
        (src / "a.conf").write_text("new-a", encoding="utf-8")
        return src

    def test_directory_swap_replaces_old_files(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            dest.mkdir(parents=True)
            (dest / "stale.conf").write_text("old", encoding="utf-8")
            self.assertTrue(atomic_replace_item(src, dest))
            self.assertEqual((dest / "a.conf").read_text(encoding="utf-8"), "new-a")
            self.assertFalse((dest / "stale.conf").exists())

    def test_dunder_file_preserved_across_swap(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            dest.mkdir(parents=True)
            (dest / "user__custom__.conf").write_text("mine", encoding="utf-8")
            self.assertTrue(atomic_replace_item(src, dest))
            self.assertEqual((dest / "user__custom__.conf").read_text(encoding="utf-8"), "mine")
            self.assertTrue((dest / "a.conf").exists())

    def test_dunder_directory_preserved(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            (dest / "extra__custom__").mkdir(parents=True)
            (dest / "extra__custom__" / "x.conf").write_text("mine", encoding="utf-8")
            self.assertTrue(atomic_replace_item(src, dest))
            self.assertEqual((dest / "extra__custom__" / "x.conf").read_text(encoding="utf-8"), "mine")

    def test_manifest_preserve_by_name(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            dest.mkdir(parents=True)
            (dest / "monitor.conf").write_text("my-monitor", encoding="utf-8")
            self.assertTrue(atomic_replace_item(src, dest, preserve=["monitor.conf"]))
            self.assertEqual((dest / "monitor.conf").read_text(encoding="utf-8"), "my-monitor")

    def test_symlink_preserve_kept_as_link(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            dest.mkdir(parents=True)
            (dest / "normal.conf").write_text("n", encoding="utf-8")
            (dest / "effects.conf").symlink_to("normal.conf")
            self.assertTrue(atomic_replace_item(src, dest, preserve=["effects.conf"]))
            self.assertTrue((dest / "effects.conf").is_symlink())
            self.assertEqual((dest / "effects.conf").readlink().name, "normal.conf")

    def test_manifest_preserve_directory(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            (dest / "themes").mkdir(parents=True)
            (dest / "themes" / "user.toml").write_text("mine", encoding="utf-8")
            self.assertTrue(atomic_replace_item(src, dest, preserve=["themes"]))
            self.assertEqual((dest / "themes" / "user.toml").read_text(encoding="utf-8"), "mine")
            self.assertTrue((dest / "a.conf").exists())

    def test_file_app_copies_content(self):
        with TempEnv() as t:
            src = t.home / "spaceship.toml"
            src.write_text("[x]", encoding="utf-8")
            dest = t.home / ".config" / "spaceship.toml"
            self.assertTrue(atomic_replace_item(src, dest))
            self.assertEqual(dest.read_text(encoding="utf-8"), "[x]")

    def test_failure_rolls_back_and_keeps_dest(self):
        with TempEnv() as t:
            src = self._src(t.home, "app")
            dest = t.home / ".config" / "app"
            dest.mkdir(parents=True)
            (dest / "keep.conf").write_text("keep", encoding="utf-8")
            with patch("zekniri.deploy.atomic.shutil.copytree", side_effect=OSError("boom")):
                self.assertFalse(atomic_replace_item(src, dest))
            self.assertEqual((dest / "keep.conf").read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
