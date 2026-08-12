import os
import tempfile
import unittest

import database


class DatabaseAuthTests(unittest.TestCase):
    def setUp(self):
        self._original_db_path = database.DB_PATH
        self._temp_dir = tempfile.TemporaryDirectory()
        database.DB_PATH = os.path.join(self._temp_dir.name, 'auth-test.db')
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self._original_db_path
        self._temp_dir.cleanup()

    def test_registered_user_can_log_in_immediately(self):
        registered, _message = database.register_user('neo', 'matrix42')
        logged_in, user = database.login_user('neo', 'matrix42')

        self.assertTrue(registered)
        self.assertTrue(logged_in)
        self.assertEqual(user['username'], 'neo')

    def test_login_trims_username_but_not_password(self):
        database.register_user('runner', ' cyber')

        logged_in, _user = database.login_user('  runner  ', ' cyber')

        self.assertTrue(logged_in)

    def test_login_reports_wrong_password_for_existing_account(self):
        database.register_user('runner', ' cyber')

        logged_in, message = database.login_user('runner', 'cyber')

        self.assertFalse(logged_in)
        self.assertEqual(message, database.t("login_password_wrong"))

    def test_login_reports_missing_account(self):
        database.register_user('runner', ' cyber')

        logged_in, message = database.login_user('ssr', 'cyber')

        self.assertFalse(logged_in)
        self.assertEqual(message, database.t("login_user_missing"))


if __name__ == '__main__':
    unittest.main()
