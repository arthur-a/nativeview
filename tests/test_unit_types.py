import unittest
from datetime import datetime, date

import dateutil.tz

from nativeview import (
    ValidationError, Integer, DateTime, Date, String)


UTC = dateutil.tz.gettz('UTC')


class TestInteger(unittest.TestCase):
    def setUp(self):
        self.type = Integer()

    def test_serialize_ok(self):
        self.assertEqual(self.type.serialize(1), 1)
        self.assertEqual(self.type.serialize('1'), 1)

    def test_serialize_fails(self):
        self.assertRaises(ValueError, self.type.serialize, 'Broken')

    def test_deserialize_ok(self):
        self.assertEqual(self.type.deserialize(1), 1)
        self.assertEqual(self.type.deserialize('1'), 1)

    def test_deserialize_fails(self):
        self.assertRaises(ValidationError, self.type.deserialize, 'Broken')


class TestDateTime(unittest.TestCase):
    def setUp(self):
        self.type = DateTime()

    def test_serialize_ok(self):
        self.assertEqual(
            self.type.serialize(
                datetime(2014, 11, 24, 21, 46, 10, 20)),
            '2014-11-24T21:46:10-00:00')

    def test_serialize_fails(self):
        self.assertRaises(ValueError, self.type.serialize, 'Broken')

    def test_deserialize_ok(self):
        self.assertEqual(
            self.type.deserialize('2014-11-24T21:46:10-00:00'),
            datetime(2014, 11, 24, 21, 46, 10, 0, UTC))

    def test_deserialize_fails(self):
        self.assertRaises(ValidationError, self.type.deserialize, 'Broken')


class TestDate(unittest.TestCase):
    def setUp(self):
        self.type = Date()

    def test_serialize_ok(self):
        self.assertEqual(
            self.type.serialize(date(2014, 11, 24)), '2014-11-24')

    def test_serialize_fails(self):
        self.assertRaises(ValueError, self.type.serialize, 'Broken')

    def test_deserialize_ok(self):
        self.assertEqual(
            self.type.deserialize('2014-11-24'),
            date(2014, 11, 24))

    def test_deserialize_fails(self):
        self.assertRaises(ValidationError, self.type.deserialize, 'Broken')


class TestString(unittest.TestCase):
    def setUp(self):
        self.type = String()

    def test_serialize_ok(self):
        self.assertEqual(
            self.type.serialize('Native string'), 'Native string')

        self.assertEqual(
            self.type.serialize(u'Unicode string'), u'Unicode string')

        self.assertEqual(
            self.type.serialize(123), u'123')

    def test_deserialize_ok(self):
        self.assertEqual(
            self.type.deserialize('Native string'), 'Native string')

        self.assertEqual(
            self.type.deserialize(u'Unicode string'), u'Unicode string')

        self.assertEqual(
            self.type.deserialize(123), u'123')
