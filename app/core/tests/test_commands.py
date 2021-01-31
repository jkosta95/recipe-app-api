from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class Command(TestCase):


    def test_wait_for_db_ready(self):
        """
            Test waiting for db when db is available.
            We will simulate connection to the database and check whether
            we have some operational error or not.
            If we have an error, db is unavailable.
            In this method we override the behavior of the ConnectionHandler.
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            # wait_for_db is going to be the name of the management command
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """
            Test waiting for db. This test will try the database five times and
            then on the sixth time it'll be successful and it will continue.
            By using patch as a decorator we passed the return_value as part
            of the function call.
            The mock (patck) replaces the behavior of time.sleep and just
            replaces with the mock function that returns True
            It won't actually wait the second or however long you have to
            wait in your code.
            The reason is just to speed up the test
        """
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.side_effect = [OperationalError] * 5 + [True] #first 5 time it will raise error
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
