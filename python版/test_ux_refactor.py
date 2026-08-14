"""Regression tests for the UX refactor (theme, window fitting, incremental draw)."""
import unittest
import tkinter as tk

from game import GameFrame, MinesweeperGame
from solver import is_no_guess
from ui_theme import COLORS, DARK_COLORS, LIGHT_COLORS, apply_theme, fit_window, get_theme


class ThemeTests(unittest.TestCase):
    def tearDown(self):
        apply_theme("dark")

    def test_apply_theme_swaps_palette(self):
        self.assertEqual(set(DARK_COLORS), set(LIGHT_COLORS))
        apply_theme("light")
        self.assertEqual(get_theme(), "light")
        self.assertEqual(COLORS["bg"], LIGHT_COLORS["bg"])
        apply_theme("dark")
        self.assertEqual(get_theme(), "dark")
        self.assertEqual(COLORS["bg"], DARK_COLORS["bg"])


class WindowTests(unittest.TestCase):
    def test_fit_window_clamps_oversized_request(self):
        root = tk.Tk()
        root.withdraw()
        try:
            fit_window(root, 5000, 5000, 300, 200)
            root.update_idletasks()
            self.assertLessEqual(root.winfo_width(), root.winfo_screenwidth())
            self.assertLessEqual(root.winfo_height(), root.winfo_screenheight())
        finally:
            root.destroy()


class NoGuessTests(unittest.TestCase):
    def test_generated_board_is_no_guess(self):
        for difficulty in ("9x9", "27x27"):
            game = MinesweeperGame(difficulty)
            game.generate_mines(0, 0)
            self.assertTrue(
                is_no_guess(game.rows, game.cols, game.board, game.mine_positions, 0, 0),
                difficulty,
            )


class IncrementalDrawTests(unittest.TestCase):
    def test_incremental_redraw_keeps_item_count_bounded(self):
        root = tk.Tk()
        try:
            frame = GameFrame(root, {"id": 1, "username": "t"}, "81x81", lambda: None)
            root.update()
            base = len(frame.canvas.find_all())
            frame.game.revealed[0][0] = True
            frame._redraw()
            root.update()
            after = len(frame.canvas.find_all())
            self.assertLess(after, base + 10)
            frame.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
