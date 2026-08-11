import tkinter as tk
import unittest
from unittest.mock import patch

from auth import AuthFrame


class AuthLayoutTests(unittest.TestCase):
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

    def test_quick_start_button_is_inside_login_card(self):
        root = tk.Tk()
        root.geometry('520x680')
        with patch('auth.os.path.exists', return_value=False):
            frame = AuthFrame(root, lambda user: None)
        frame.pack(fill=tk.BOTH, expand=True)
        root.update()

        quick_button = frame.quick_start_button
        card = frame._auth_card
        quick_bottom = quick_button.winfo_rooty() + quick_button.winfo_height()
        card_bottom = card.winfo_rooty() + card.winfo_height()

        self.assertGreater(quick_button.winfo_height(), 1)
        self.assertLessEqual(quick_bottom, card_bottom)
        root.destroy()


if __name__ == '__main__':
    unittest.main()
