import unittest

from tests.utils import TempEnv
from zekniri.deploy.templates import _phase_render_templates, _render_file, PLACEHOLDER


class TemplatesTest(unittest.TestCase):
    def test_placeholder_replaced_after_deploy(self):
        with TempEnv() as t:
            src = t.home / "configs" / "app"
            src.mkdir(parents=True)
            (src / "conf").write_text(f"path = {PLACEHOLDER}/x", encoding="utf-8")
            from zekniri.deploy.deploy import deploy_selected_configs
            deploy_selected_configs(items_to_deploy=["app"])
            deployed = t.home / ".config" / "app" / "conf"
            self.assertIn(str(t.home), deployed.read_text(encoding="utf-8"))
            self.assertNotIn(PLACEHOLDER, deployed.read_text(encoding="utf-8"))

    def test_render_file_no_placeholder_is_noop(self):
        with TempEnv() as t:
            f = t.home / "plain.conf"
            f.write_text("nothing here", encoding="utf-8")
            self.assertFalse(_render_file(f, str(t.home)))
            self.assertEqual(f.read_text(encoding="utf-8"), "nothing here")

    def test_only_app_scopes_render(self):
        with TempEnv() as t:
            a = t.home / ".config" / "a"
            b = t.home / ".config" / "b"
            a.mkdir(parents=True)
            b.mkdir(parents=True)
            (a / "c").write_text(PLACEHOLDER, encoding="utf-8")
            (b / "c").write_text(PLACEHOLDER, encoding="utf-8")
            _phase_render_templates(only_app="a")
            self.assertNotIn(PLACEHOLDER, (a / "c").read_text(encoding="utf-8"))
            self.assertIn(PLACEHOLDER, (b / "c").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
