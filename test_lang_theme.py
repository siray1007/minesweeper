import unittest

from lang import LANG_OPTIONS, TEXTS
from ui_theme import COLORS, draw_grid_background, make_panel, metric_label


class LanguageThemeTests(unittest.TestCase):
    def test_core_language_keys_exist(self):
        required = {
            "title", "login", "register", "menu_title", "rank_title",
            "btn_start", "btn_restart", "btn_ranking", "btn_logout", "btn_quick_start", "btn_account",
            "status_local_loaded", "status_cloud_done", "control_hint",
            "auth_kicker", "auth_status", "menu_subtitle", "mine_density", "mine_count_label", "quick_controls",
            "board_status_ready", "rank_empty_marker", "clearance_label", "flags_label",
            "best_label", "ops_label", "btn_lobby", "btn_result_records", "result_summary",
            "profile_subtitle", "profile_total_matches", "profile_wins", "profile_losses",
            "profile_win_rate", "profile_recent_title", "profile_no_recent",
            "profile_switch_account", "match_win", "match_fail",
        }
        for lang, mapping in TEXTS.items():
            self.assertTrue(required.issubset(mapping), lang)

    def test_language_options_point_to_existing_tables(self):
        for code, _name in LANG_OPTIONS:
            self.assertIn(code, TEXTS)

    def test_theme_has_core_tokens(self):
        for key in (
            "bg", "bg_grid", "surface", "surface_alt", "surface_metal", "border",
            "border_hot", "border_dim", "text", "muted", "primary", "danger",
            "tile_even", "tile_odd", "tile_open", "tile_flag",
        ):
            self.assertIn(key, COLORS)

    def test_theme_exports_polish_helpers(self):
        self.assertTrue(callable(make_panel))
        self.assertTrue(callable(metric_label))
        self.assertTrue(callable(draw_grid_background))


if __name__ == "__main__":
    unittest.main()
