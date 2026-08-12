import os
import tempfile
import tkinter as tk
import unittest

from auth import AuthFrame
import database
from main import MainApp
from lang import t


class MainFlowTests(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.db_path)
        self.original_path = database.DB_PATH
        database.DB_PATH = self.db_path

    def tearDown(self):
        database.DB_PATH = self.original_path
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def _logged_in_app(self):
        app = MainApp(start_loop=False)
        database.register_user("NeonRunner", "matrix42")
        ok, user = database.login_user("NeonRunner", "matrix42")
        self.assertTrue(ok)
        app._on_login(user)
        return app

    def test_app_opens_at_authentication_gate(self):
        app = MainApp(start_loop=False)
        try:
            app.root.update()
            self.assertIsNone(app.current_user)
            self.assertIsInstance(app.current_frame, AuthFrame)
            self.assertGreaterEqual(app.root.winfo_width(), 560)
            self.assertGreaterEqual(app.root.winfo_height(), 680)
        finally:
            app.root.destroy()

    def test_profile_panel_opens_with_personal_summary(self):
        app = self._logged_in_app()
        try:
            database.save_ranking(app.current_user["id"], "9x9", 42)
            database.save_match_result(app.current_user["id"], "9x9", "win", 42)
            database.save_match_result(app.current_user["id"], "27x27", "game_over", 17)

            app._show_profile()
            app.root.update()

            self.assertIsNotNone(app._profile_dialog)
            self.assertTrue(app._profile_dialog.winfo_exists())
            self.assertEqual(app._profile_summary["total_matches"], 2)
            self.assertEqual(app._profile_summary["wins"], 1)
            self.assertGreaterEqual(app._profile_switch_button.winfo_height(), 56)
            self.assertGreaterEqual(app._profile_logout_button.winfo_height(), 56)
            self.assertEqual(app._profile_switch_button.winfo_width(), app._profile_logout_button.winfo_width())
            self.assertTrue(app._profile_switch_button.winfo_viewable())
            self.assertTrue(app._profile_logout_button.winfo_viewable())
            dialog_bottom = app._profile_dialog.winfo_rooty() + app._profile_dialog.winfo_height()
            button_bottom = app._profile_switch_button.winfo_rooty() + app._profile_switch_button.winfo_height()
            self.assertLessEqual(button_bottom, dialog_bottom)
        finally:
            app._close_profile_dialog()
            app.root.destroy()

    def test_lobby_contains_only_game_content_and_one_ranking_entry(self):
        app = self._logged_in_app()
        try:
            app.root.update()

            texts = []
            pending = [app.current_frame]
            while pending:
                widget = pending.pop()
                pending.extend(widget.winfo_children())
                try:
                    text = widget.cget("text")
                except tk.TclError:
                    continue
                if text:
                    texts.append(text)

            self.assertEqual(texts.count(t("profile_label")), 1)
            self.assertEqual(texts.count(t("btn_ranking")), 1)
            self.assertEqual(texts.count(app.current_user["username"]), 1)
            self.assertIn(t("lobby_records_title"), texts)
            combined = " ".join(str(text) for text in texts).lower()
            self.assertNotIn("github", combined)
            self.assertNotIn("siray1007/minesweeper", combined)
            self.assertNotIn("repository", combined)
            self.assertNotIn("仓库", combined)
        finally:
            app.root.destroy()

    def test_switch_account_returns_to_auth(self):
        app = self._logged_in_app()
        try:
            app._show_profile()
            app._switch_account()
            app.root.update()

            self.assertIsNone(app.current_user)
            self.assertIsInstance(app.current_frame, AuthFrame)
        finally:
            app.root.destroy()

    def test_logout_from_profile_returns_to_auth(self):
        app = self._logged_in_app()
        try:
            app._show_profile()
            app._logout()
            app.root.update()

            self.assertIsNone(app.current_user)
            self.assertIsInstance(app.current_frame, AuthFrame)
        finally:
            app.root.destroy()

    def test_ranking_opens_at_larger_scale(self):
        app = self._logged_in_app()
        try:
            app._show_ranking()
            app.root.update()

            self.assertGreaterEqual(app.root.winfo_width(), 1260)
            self.assertGreaterEqual(app.root.winfo_height(), 800)
        finally:
            app.root.destroy()


if __name__ == "__main__":
    unittest.main()
