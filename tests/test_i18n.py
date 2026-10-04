import ast
import unittest
from pathlib import Path

from zekniri.i18n import TRANSLATIONS

_PKG = Path(__file__).resolve().parent.parent / "zekniri"
_I18N_FILE = _PKG / "i18n.py"
_KEY_CALLS = {"msg", "prompt_confirm", "responsive_hint"}


def _iter_trees():
    for py in _PKG.rglob("*.py"):
        yield py, ast.parse(py.read_text(encoding="utf-8"), filename=str(py))


def _used_keys() -> set:
    keys = set()
    for _py, tree in _iter_trees():
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in _KEY_CALLS
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                keys.add(node.args[0].value)
    return keys


def _string_literals_outside_i18n() -> set:
    lits = set()
    for py, tree in _iter_trees():
        if py == _I18N_FILE:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                lits.add(node.value)
    return lits


class I18nTest(unittest.TestCase):
    def test_languages_have_identical_keys(self):
        zh = set(TRANSLATIONS["zh"])
        en = set(TRANSLATIONS["en"])
        self.assertEqual(zh - en, set(), "keys missing from en")
        self.assertEqual(en - zh, set(), "keys missing from zh")

    def test_no_missing_keys(self):
        used = _used_keys()
        for lang in ("zh", "en"):
            missing = used - set(TRANSLATIONS[lang])
            self.assertEqual(missing, set(), f"keys used but missing in {lang}: {missing}")

    def test_no_orphan_keys(self):
        literals = _string_literals_outside_i18n()
        orphans = set(TRANSLATIONS["en"]) - literals
        self.assertEqual(orphans, set(), f"keys defined but never referenced: {orphans}")


if __name__ == "__main__":
    unittest.main()
