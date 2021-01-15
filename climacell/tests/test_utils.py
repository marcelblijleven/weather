from datetime import datetime, timezone
from unittest import TestCase

from climacell.utils import join_fields, check_datetime_str, parse_datetime_str


class TestUtils(TestCase):
    def test_join_fields(self):
        self.assertEqual('abc,def', join_fields(['abc', 'def']))
        self.assertEqual('abc', join_fields(['abc']))
        self.assertEqual('', join_fields([]))

    def test_check_datetime_str(self):
        self.assertEqual(True, check_datetime_str('2021-01-13T23:26:32.019922'), msg='Test case 1 failed')
        self.assertEqual(True, check_datetime_str('2021-01-13T23:26:32.199Z'), msg='Test case 2 failed')
        self.assertEqual(False, check_datetime_str('now'), msg='Test case 4 failed')

    def test_parse_datetime_str(self):
        expected = datetime(2021, 1, 14, 21, tzinfo=timezone.utc)
        self.assertEqual(expected, parse_datetime_str('2021-01-14T21:00:00.000Z'))
