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


if __name__ == "__main__":
    unittest.main()
