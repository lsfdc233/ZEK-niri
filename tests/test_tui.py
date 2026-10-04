import unittest

from tests.utils import TempEnv
from zekniri import i18n
from zekniri.tui import alternate_screen, select_language


class LanguagePageTest(unittest.TestCase):
    def setUp(self):
        import zekniri.tui as tui
        tui._ALT_ACTIVE = False

    def test_first_run_has_no_stored_language(self):
        with TempEnv():
            self.assertFalse(i18n.has_stored_language())

    def test_stored_language_skips_page(self):
        with TempEnv():
            i18n.set_language("en")
            self.assertTrue(i18n.has_stored_language())
            # Non-interactive: if the page were shown this would return the
            # default; the early return proves the page is skipped on later runs.
            self.assertEqual(select_language(), "en")

    def test_choice_persisted_under_config_home(self):
        with TempEnv() as t:
            i18n.set_language("zh")
            self.assertTrue((t.home / ".config" / "ZEKniri" / "language").is_file())
            i18n._reset_language_cache()
            self.assertEqual(i18n.get_language(), "zh")
            self.assertTrue(i18n.has_stored_language())

    def test_alternate_screen_enters_and_leaves(self):
        import io
        import sys as _sys
        from unittest.mock import patch

        class FakeTTY(io.StringIO):
            def isatty(self):
                return True

        buf = FakeTTY()
        with patch.object(_sys, "stdout", buf):
            with alternate_screen():
                pass
        out = buf.getvalue()
        self.assertIn("\033[?1049h", out)
        self.assertIn("\033[?1049l", out)

    def test_alternate_screen_restores_on_exception(self):
        import io
        import sys as _sys
        from unittest.mock import patch

        class FakeTTY(io.StringIO):
            def isatty(self):
                return True

        buf = FakeTTY()
        with patch.object(_sys, "stdout", buf):
            with self.assertRaises(RuntimeError):
                with alternate_screen():
                    raise RuntimeError("boom")
        self.assertIn("\033[?1049l", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
