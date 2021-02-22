import logging
import unittest

from ohsome_quality_analyst.utils.definitions import configure_logging


class TestLogging(unittest.TestCase):
    def test_logging(self):
        configure_logging()
        with self.assertLogs() as captured:
            logging.info("Test logging message")
        # Test that there is only one log message
        self.assertEqual(len(captured.records), 1)
        # Test unformatted logging output message
        self.assertEqual(captured.records[0].getMessage(), "Test logging message")


if __name__ == "__main__":
    unittest.main()
