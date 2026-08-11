import unittest

from lang import LANG_OPTIONS, TEXTS
from ui_theme import COLORS


class LanguageThemeTests(unittest.TestCase):
    def test_core_language_keys_exist(self):
        required = {
            "title", "login", "register", "menu_title", "rank_title",
            "btn_start", "btn_restart", "btn_ranking", "btn_logout",
            "status_local_loaded", "status_cloud_done", "control_hint",
        }
        for lang, mapping in TEXTS.items():
            self.assertTrue(required.issubset(mapping), lang)

    def test_language_options_point_to_existing_tables(self):
        for code, _name in LANG_OPTIONS:
            self.assertIn(code, TEXTS)

    def test_theme_has_core_tokens(self):
        for key in ("bg", "surface", "surface_alt", "border", "text", "muted", "primary", "danger"):
            self.assertIn(key, COLORS)


if __name__ == "__main__":
    unittest.main()
