import os
import tempfile
import tkinter as tk
import unittest
from unittest.mock import patch

from auth import AuthFrame
import lang
from lang import get_lang, save_lang


class AuthLayoutTests(unittest.TestCase):
    def setUp(self):
        self.original_lang = get_lang()
        fd, self.lang_file = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        self.original_lang_file = lang._LANG_FILE
        lang._LANG_FILE = self.lang_file

    def tearDown(self):
        save_lang(self.original_lang)
        lang._LANG_FILE = self.original_lang_file
        if os.path.exists(self.lang_file):
            os.remove(self.lang_file)

    def test_registration_button_is_inside_login_card(self):
        root = tk.Tk()
        root.geometry('520x680')
        # The layout test does not depend on the decorative image. Skipping it
        # also avoids Tcl's path handling differences on Windows test hosts.
        with patch('auth.os.path.exists', return_value=False):
            frame = AuthFrame(root, lambda user: None)
        frame.pack(fill=tk.BOTH, expand=True)
        root.update()

        button = frame.register_nav_button
        card = frame._auth_card
        button_bottom = button.winfo_rooty() + button.winfo_height()
        card_bottom = card.winfo_rooty() + card.winfo_height()

        self.assertGreater(button.winfo_height(), 1)
        self.assertLessEqual(button_bottom, card_bottom)
        root.destroy()

    def test_language_switch_preserves_login_input(self):
        root = tk.Tk()
        with patch('auth.os.path.exists', return_value=False):
            frame = AuthFrame(root, lambda user: None)
        frame.pack(fill=tk.BOTH, expand=True)
        root.update()
        frame._user.insert(0, "ssr")

        frame._change_language("en")
        root.update()

        self.assertEqual(frame._user.get(), "ssr")
        self.assertEqual(get_lang(), "en")
        root.destroy()

    def test_login_failure_stays_inline(self):
        root = tk.Tk()
        with patch('auth.os.path.exists', return_value=False):
            frame = AuthFrame(root, lambda user: None)
        frame.pack(fill=tk.BOTH, expand=True)
        root.update()
        frame._user.insert(0, "ssr")
        frame._pwd.insert(0, "wrong")

        with patch('auth.login_user', return_value=(False, "bad password")):
            frame._do_login()
        root.update()

        self.assertEqual(frame._inline_message.cget("text"), "bad password")
        self.assertEqual(frame._pwd.index("sel.first"), 0)
        self.assertEqual(frame._pwd.index("sel.last"), len("wrong"))
        root.destroy()

if __name__ == '__main__':
    unittest.main()
