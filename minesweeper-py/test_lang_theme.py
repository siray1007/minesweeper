import unittest

from lang import LANG_OPTIONS, TEXTS
from ui_theme import COLORS, LAYOUT, draw_grid_background, make_panel, metric_label, section_title


class LanguageThemeTests(unittest.TestCase):
    @staticmethod
    def _luminance(color):
        red, green, blue = (int(color[index:index + 2], 16) for index in (1, 3, 5))
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    def test_core_language_keys_exist(self):
        required = {
            "title", "login", "register", "menu_title", "rank_title",
            "btn_start", "btn_restart", "btn_ranking", "btn_logout", "btn_account",
            "status_local_loaded", "status_cloud_done", "control_hint",
            "auth_kicker", "auth_status", "menu_subtitle", "mine_density", "mine_count_label", "quick_controls",
            "board_status_ready", "rank_empty_marker", "clearance_label", "flags_label",
            "best_label", "ops_label", "btn_lobby", "btn_result_records", "result_summary",
            "profile_subtitle", "profile_total_matches", "profile_wins", "profile_losses",
            "profile_win_rate", "profile_recent_title", "profile_no_recent",
            "profile_switch_account", "match_win", "match_fail",
            "status_cloud_failed", "auth_ready", "lobby_controls",
            "result_retry_tip",
            "lobby_records_title", "lobby_records_subtitle",
        }
        for lang, mapping in TEXTS.items():
            self.assertTrue(required.issubset(mapping), lang)

    def test_language_options_point_to_existing_tables(self):
        for code, _name in LANG_OPTIONS:
            self.assertIn(code, TEXTS)
        self.assertEqual(len(LANG_OPTIONS), 14)
        self.assertEqual([code for code, _name in LANG_OPTIONS], [
            "zh", "zh-TW", "en", "ja", "ko", "es", "fr", "de", "pt", "ru", "ar", "hi", "it", "lzh"
        ])
        self.assertEqual(TEXTS["zh"]["title"], "扫雷")
        self.assertEqual(TEXTS["zh-TW"]["title"], "掃雷")
        self.assertEqual(TEXTS["lzh"]["title"], "掃雷")
        self.assertEqual(set(TEXTS), set(code for code, _name in LANG_OPTIONS))

    def test_every_locale_has_complete_resource_keys(self):
        required = set(TEXTS["zh"])
        for code, mapping in TEXTS.items():
            self.assertEqual(required, set(mapping), code)

    def test_language_aliases_preserve_old_preferences(self):
        from lang import _normalize_lang

        self.assertEqual(_normalize_lang("zt"), "zh-TW")
        self.assertEqual(_normalize_lang("wy"), "lzh")
        self.assertEqual(_normalize_lang("unknown"), "zh")

    def test_product_name_is_minesweeper_not_style_name(self):
        self.assertEqual(TEXTS["zh"]["title"], "扫雷")
        self.assertEqual(TEXTS["en"]["title"], "Minesweeper")
        self.assertNotIn("赛博", TEXTS["zh"]["title"])
        self.assertNotIn("Cyber", TEXTS["en"]["title"])
        self.assertTrue(TEXTS["zh"]["auth_kicker"].startswith("MINESWEEPER"))

    def test_lzh_reads_like_meaningful_classical_chinese(self):
        lzh = TEXTS["lzh"]
        self.assertEqual(lzh["title"], "掃雷")
        self.assertEqual(lzh["login"], "入局")
        self.assertEqual(lzh["btn_start"], "出戰")
        self.assertEqual(lzh["game_over"], "局敗")
        self.assertEqual(lzh["win_title"], "局成")
        self.assertIn("雷區", lzh["menu_subtitle"])
        self.assertIn("雲端", lzh["status_cloud_done"])
        self.assertNotIn("Cyber", lzh["auth_kicker"])

    def test_theme_has_core_tokens(self):
        for key in (
            "bg", "bg_grid", "surface", "surface_alt", "surface_metal", "border",
            "border_hot", "border_dim", "text", "muted", "primary", "danger",
            "tile_even", "tile_odd", "tile_open", "tile_flag",
            "tile_border", "tile_open_border", "tile_open_alt",
        ):
            self.assertIn(key, COLORS)

    def test_theme_exports_polish_helpers(self):
        self.assertTrue(callable(make_panel))
        self.assertTrue(callable(metric_label))
        self.assertTrue(callable(draw_grid_background))
        self.assertTrue(callable(section_title))
        self.assertGreaterEqual(LAYOUT["lobby"][0], 1280)
        self.assertGreaterEqual(LAYOUT["profile"][0], 1000)

    def test_theme_is_bright_layered_and_not_near_black(self):
        self.assertGreater(self._luminance(COLORS["bg"]), 35)
        self.assertGreater(self._luminance(COLORS["surface"]), self._luminance(COLORS["bg"]))
        self.assertGreater(self._luminance(COLORS["surface_alt"]), self._luminance(COLORS["surface"]))
        self.assertGreater(self._luminance(COLORS["text"]) - self._luminance(COLORS["surface"]), 140)


if __name__ == "__main__":
    unittest.main()
