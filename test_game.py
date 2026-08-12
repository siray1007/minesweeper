import random
import unittest

from game import MinesweeperGame, calculate_fit_zoom


class MinesweeperGameTests(unittest.TestCase):
    def test_fit_zoom_uses_both_viewport_dimensions(self):
        self.assertEqual(calculate_fit_zoom(1000, 600, 81, 81, 16), 0.46)
        self.assertEqual(calculate_fit_zoom(600, 1000, 81, 81, 16), 0.46)

    def test_fit_zoom_stays_inside_supported_range(self):
        self.assertEqual(calculate_fit_zoom(100, 100, 81, 81, 16), 0.25)
        self.assertEqual(calculate_fit_zoom(8000, 8000, 9, 9, 16), 3.0)

    def test_rejects_unknown_difficulty(self):
        with self.assertRaises(ValueError):
            MinesweeperGame('custom')

    def test_first_reveal_generates_mines_outside_safe_zone(self):
        game = MinesweeperGame('9x9', rng=random.Random(7))

        result = game.reveal(4, 4)

        self.assertIn(result, {'continue', 'win'})
        self.assertTrue(game.mines_generated)
        self.assertEqual(len(game.mine_positions), 10)
        self.assertFalse(any(abs(r - 4) <= 1 and abs(c - 4) <= 1
                             for r, c in game.mine_positions))
        self.assertEqual(
            sum(game.board[r][c] == -1 for r in range(game.rows)
                for c in range(game.cols)),
            10,
        )

    def test_flagged_cell_cannot_be_revealed_and_count_updates(self):
        game = MinesweeperGame('9x9', rng=random.Random(1))

        game.toggle_flag(0, 0)
        self.assertEqual(game.remaining_mines, 9)
        self.assertEqual(game.reveal(0, 0), 'continue')
        self.assertFalse(game.revealed[0][0])

        game.toggle_flag(0, 0)
        self.assertEqual(game.remaining_mines, 10)

    def test_revealing_a_known_mine_ends_game(self):
        game = MinesweeperGame('9x9', rng=random.Random(1))
        game.reveal(0, 0)
        mine = next(iter(game.mine_positions))

        self.assertEqual(game.reveal(*mine), 'game_over')
        self.assertTrue(game.game_over)
        self.assertTrue(game.revealed[mine[0]][mine[1]])

    def test_out_of_bounds_chord_is_safe(self):
        game = MinesweeperGame('9x9', rng=random.Random(1))

        self.assertEqual(game.chord(-1, 0), 'continue')
        self.assertEqual(game.chord(game.rows, game.cols), 'continue')

    def test_all_safe_cells_can_be_revealed_to_win(self):
        game = MinesweeperGame('9x9', rng=random.Random(2))
        game.reveal(0, 0)

        final = 'continue'
        for row in range(game.rows):
            for col in range(game.cols):
                if (row, col) not in game.mine_positions:
                    final = game.reveal(row, col)
                    if final == 'win':
                        break
            if final == 'win':
                break

        self.assertEqual(final, 'win')
        self.assertTrue(game.game_won)
        self.assertEqual(game.revealed_count, game.total_safe_cells)


if __name__ == '__main__':
    unittest.main()
