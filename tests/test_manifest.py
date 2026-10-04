import os
import tempfile
import unittest
from pathlib import Path

from tests.utils import TempEnv
from zekniri.deploy.manifest import (
    load_manifest,
    load_optional_apps,
    discover_deployable_apps,
    discover_optional_apps,
)


class ManifestTest(unittest.TestCase):
    def _app(self, configs: Path, name: str) -> Path:
        app = configs / name
        app.mkdir(parents=True)
        (app / "conf").write_text("x", encoding="utf-8")
        return app

    def test_defaults_from_dir_name(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            app = self._app(configs, "kitty")
            m = load_manifest(app)
            self.assertEqual(m.packages_repo, ["kitty"])
            self.assertEqual(m.label, "kitty")
            self.assertEqual(m.detect, "kitty")
            self.assertEqual(m.preserve, [])
            self.assertTrue(m.is_deployable)
            self.assertFalse(m.is_optional)

    def test_manifest_overrides(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            app = self._app(configs, "wm")
            (app / ".module.toml").write_text(
                '[packages]\nlabel = "Window Manager"\npreserve = ["monitor.conf"]\nchmod = ["scripts/*.sh"]\n',
                encoding="utf-8",
            )
            m = load_manifest(app)
            self.assertEqual(m.label, "Window Manager")
            self.assertEqual(m.preserve, ["monitor.conf"])
            self.assertEqual(m.chmod, ["scripts/*.sh"])

    def test_file_type_sidecar(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            f = configs / "prompt.toml"
            f.write_text("x", encoding="utf-8")
            (configs / "prompt.toml.module.toml").write_text(
                '[packages]\nrepo = ["prompt"]\ndetect = "prompt"\n', encoding="utf-8"
            )
            m = load_manifest(f)
            self.assertEqual(m.packages_repo, ["prompt"])
            self.assertTrue(m.is_deployable)

    def test_optional_apps_parsed_and_merged(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            self._app(configs, "editor")  # dual: has config + optional
            (configs / ".optional-apps.toml").write_text(
                '[[app]]\nname = "editor"\nlabel = "Editor"\ncategory = "dev"\n'
                '[[app]]\nname = "browser"\nrepo = ["firefox"]\n',
                encoding="utf-8",
            )
            optional = load_optional_apps()
            self.assertIn("editor", optional)
            self.assertIn("browser", optional)

            deployable = discover_deployable_apps()
            self.assertIn("editor", deployable)
            self.assertNotIn("browser", deployable)

            optional_names = discover_optional_apps()
            self.assertIn("editor", optional_names)
            self.assertIn("browser", optional_names)

    def test_hidden_entries_ignored(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            (configs / ".gitkeep").write_text("", encoding="utf-8")
            self._app(configs, "real")
            self.assertEqual(discover_deployable_apps(), ["real"])

    def test_bad_toml_does_not_break_discovery(self):
        with TempEnv() as t:
            configs = t.home / "configs"
            configs.mkdir(exist_ok=True)
            self._app(configs, "good")
            bad = self._app(configs, "bad")
            (bad / ".module.toml").write_text("this is = not toml [", encoding="utf-8")
            names = discover_deployable_apps()
            self.assertIn("good", names)
            self.assertNotIn("bad", names)  # skipped, not fatal


if __name__ == "__main__":
    unittest.main()
