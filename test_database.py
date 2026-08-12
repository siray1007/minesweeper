import os
import tempfile
import unittest

import database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.remove(self.db_path)
        self.original_path = database.DB_PATH
        database.DB_PATH = self.db_path
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self.original_path
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_quick_local_user_is_created_and_reused(self):
        first = database.get_or_create_local_user()
        second = database.get_or_create_local_user()

        self.assertEqual(first["username"], "CyberPilot")
        self.assertEqual(first, second)

    def test_profile_summary_tracks_results_and_best_times(self):
        user = database.get_or_create_local_user("NeonRunner")
        database.save_ranking(user["id"], "9x9", 42)
        database.save_match_result(user["id"], "9x9", "win", 42)
        database.save_match_result(user["id"], "27x27", "game_over", 17)

        summary = database.get_user_profile_summary(user["id"])

        self.assertEqual(summary["total_matches"], 2)
        self.assertEqual(summary["wins"], 1)
        self.assertEqual(summary["losses"], 1)
        self.assertEqual(summary["win_rate"], 50)
        self.assertEqual(summary["best_by_difficulty"]["9x9"], 42)
        self.assertEqual(summary["run_counts"]["9x9"], 1)
        self.assertEqual(summary["run_counts"]["27x27"], 1)
        self.assertEqual(len(summary["recent_matches"]), 2)

    def test_existing_rankings_seed_profile_history(self):
        user = database.get_or_create_local_user("ArchivePilot")
        database.save_ranking(user["id"], "9x9", 35)

        database.init_db()
        summary = database.get_user_profile_summary(user["id"])

        self.assertEqual(summary["total_matches"], 1)
        self.assertEqual(summary["wins"], 1)
        self.assertEqual(summary["losses"], 0)
        self.assertEqual(summary["run_counts"]["9x9"], 1)


if __name__ == "__main__":
    unittest.main()
