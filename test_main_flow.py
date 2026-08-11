import os
import tempfile
import tkinter as tk
import unittest

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
        finally:
            app.root.destroy()


if __name__ == "__main__":
    unittest.main()
