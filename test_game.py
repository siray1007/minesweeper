import random
import tkinter as tk
import unittest

from game import DIFFICULTY_CONFIG, GameFrame, MinesweeperGame, board_density, clearance_percent, flag_count


class MinesweeperGameTests(unittest.TestCase):
    def test_board_density_uses_mine_ratio(self):
        self.assertEqual(board_density(DIFFICULTY_CONFIG["9x9"]), "12.3%")
        self.assertEqual(board_density(DIFFICULTY_CONFIG["27x27"]), "13.7%")

    def test_hud_helpers_track_clearance_and_flags(self):
        game = MinesweeperGame("9x9", rng=random.Random(11))

        self.assertEqual(clearance_percent(game), 0)
        self.assertEqual(flag_count(game), 0)

        game.toggle_flag(0, 0)
        game.reveal(4, 4)

        self.assertEqual(flag_count(game), 1)
        self.assertGreaterEqual(clearance_percent(game), 1)
        self.assertLessEqual(clearance_percent(game), 100)

    def test_rejects_unknown_difficulty(self):
        with self.assertRaises(ValueError):
            MinesweeperGame("custom")

    def test_first_reveal_generates_mines_outside_safe_zone(self):
        game = MinesweeperGame("9x9", rng=random.Random(7))

        result = game.reveal(4, 4)

        self.assertIn(result, {"continue", "win"})
        self.assertTrue(game.mines_generated)
        self.assertEqual(len(game.mine_positions), 10)
        self.assertFalse(any(abs(r - 4) <= 1 and abs(c - 4) <= 1 for r, c in game.mine_positions))
        self.assertEqual(
            sum(game.board[r][c] == -1 for r in range(game.rows) for c in range(game.cols)),
            10,
        )

    def test_flagged_cell_cannot_be_revealed_and_count_updates(self):
        game = MinesweeperGame("9x9", rng=random.Random(1))

        game.toggle_flag(0, 0)
        self.assertEqual(game.remaining_mines, 9)
        self.assertEqual(game.reveal(0, 0), "continue")
        self.assertFalse(game.revealed[0][0])

        game.toggle_flag(0, 0)
        self.assertEqual(game.remaining_mines, 10)

    def test_revealing_a_known_mine_ends_game(self):
        game = MinesweeperGame("9x9", rng=random.Random(1))
        game.reveal(0, 0)
        mine = next(iter(game.mine_positions))

        self.assertEqual(game.reveal(*mine), "game_over")
        self.assertTrue(game.game_over)
        self.assertTrue(game.revealed[mine[0]][mine[1]])

    def test_out_of_bounds_chord_is_safe(self):
        game = MinesweeperGame("9x9", rng=random.Random(1))

        self.assertEqual(game.chord(-1, 0), "continue")
        self.assertEqual(game.chord(game.rows, game.cols), "continue")

    def test_all_safe_cells_can_be_revealed_to_win(self):
        game = MinesweeperGame("9x9", rng=random.Random(2))
        game.reveal(0, 0)

        final = "continue"
        for row in range(game.rows):
            for col in range(game.cols):
                if (row, col) not in game.mine_positions:
                    final = game.reveal(row, col)
                    if final == "win":
                        break
            if final == "win":
                break

        self.assertEqual(final, "win")
        self.assertTrue(game.game_won)
        self.assertEqual(game.revealed_count, game.total_safe_cells)

    def test_result_panel_is_embedded(self):
        root = tk.Tk()
        frame = GameFrame(root, {"id": 1, "username": "ssr"}, "9x9", lambda: None)
        frame.pack(fill=tk.BOTH, expand=True)
        root.update()

        frame._show_result_panel("game_over")
        root.update()

        self.assertIsNotNone(frame._result_panel)
        self.assertTrue(frame._result_panel.winfo_exists())
        self.assertIs(frame._result_panel.winfo_toplevel(), root)
        root.destroy()


if __name__ == "__main__":
    unittest.main()
