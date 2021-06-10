import datetime
import unittest

from ohsome_quality_analyst.utils.helper import datetime_to_isostring_timestamp


class TestDatetimeToIsostring(unittest.TestCase):
    def test_valid_input_datetime(self):
        self.assertIsInstance(
            datetime_to_isostring_timestamp(datetime.datetime.now()), str
        )

    def test_valid_input_date(self):
        self.assertIsInstance(
            datetime_to_isostring_timestamp(datetime.date.today()), str
        )

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            datetime_to_isostring_timestamp("foo")


if __name__ == "__main__":
    unittest.main()
