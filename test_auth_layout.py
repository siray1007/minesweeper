import tkinter as tk
import unittest
from unittest.mock import patch

from auth import AuthFrame
from lang import LANG_OPTIONS, TEXTS
from ui_theme import COLORS, LAYOUT, section_title


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

    def test_grand_scale_layout_tokens_are_present(self):
        self.assertGreaterEqual(LAYOUT['auth']['window'][0], 760)
        self.assertGreaterEqual(LAYOUT['lobby']['window'][0], 1280)
        self.assertGreaterEqual(LAYOUT['ranking']['window'][0], 1200)
        self.assertIn('primary', COLORS)
        self.assertIn('surface_alt', COLORS)

    def test_visible_language_options_have_complete_text(self):
        required = {
            'title', 'login', 'register', 'menu_title', 'rank_title',
            'btn_start', 'btn_restart', 'btn_ranking', 'btn_logout',
            'lobby_launch_title', 'lobby_status_title',
        }
        for lang, _name in LANG_OPTIONS:
            self.assertTrue(required.issubset(TEXTS[lang]), lang)

    def test_section_title_helper_renders_heading(self):
        root = tk.Tk()
        frame = tk.Frame(root, bg=COLORS['bg'])
        frame.pack()
        block = section_title(frame, '战场', '在线')
        block.pack()
        root.update()

        labels = block.winfo_children()
        self.assertEqual(labels[0].cget('text'), '战场')
        self.assertEqual(labels[1].cget('text'), '在线')
        root.destroy()


if __name__ == '__main__':
    unittest.main()
