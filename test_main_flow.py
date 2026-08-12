import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from auth import AuthFrame
import database
from main import MainApp


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

    def test_app_opens_directly_to_local_lobby(self):
        app = MainApp(start_loop=False)
        try:
            app.root.update()
            self.assertEqual(app.current_user["username"], "CyberPilot")
            self.assertIsInstance(app.current_frame, tk.Frame)
            self.assertIn("CyberPilot", str(app.current_user))
            self.assertGreaterEqual(app.root.winfo_width(), 1320)
            self.assertGreaterEqual(app.root.winfo_height(), 840)
        finally:
            app.root.destroy()

    def test_profile_panel_opens_with_personal_summary(self):
        app = MainApp(start_loop=False)
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
        finally:
            app._close_profile_dialog()
            app.root.destroy()

    def test_switch_account_returns_to_auth(self):
        app = MainApp(start_loop=False)
        try:
            app._show_profile()
            app._switch_account()
            app.root.update()

            self.assertIsNone(app.current_user)
            self.assertIsInstance(app.current_frame, AuthFrame)
        finally:
            app.root.destroy()

    def test_logout_from_profile_returns_to_auth(self):
        app = MainApp(start_loop=False)
        try:
            app._show_profile()
            with patch("main.messagebox.askyesno", return_value=True):
                app._logout()
            app.root.update()

            self.assertIsNone(app.current_user)
            self.assertIsInstance(app.current_frame, AuthFrame)
        finally:
            app.root.destroy()

    def test_ranking_opens_at_larger_scale(self):
        app = MainApp(start_loop=False)
        try:
            app._show_ranking()
            app.root.update()

            self.assertGreaterEqual(app.root.winfo_width(), 1260)
            self.assertGreaterEqual(app.root.winfo_height(), 800)
        finally:
            app.root.destroy()


if __name__ == "__main__":
    unittest.main()
