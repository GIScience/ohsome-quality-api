import logging
import os
import sys
import unittest

from ohsome_quality_api.config import configure_logging


class TestLogging(unittest.TestCase):
    def setUp(self):
        self.log_level = os.environ.pop("OQAPI_LOG_LEVEL", None)

    def tearDown(self):
        if self.log_level is not None:
            os.environ["OQAPI_LOG_LEVEL"] = self.log_level
        else:
            os.environ.pop("OQAPI_LOG_LEVEL", None)

    def test_logging(self):
        configure_logging()
        with self.assertLogs(level="INFO") as captured:
            logging.info("Test info logging message")
            logging.debug("Test debug logging message")
        # Test that there is only one log message
        self.assertEqual(len(captured.records), 1)
        # Test not-formatted logging output message
        self.assertEqual(captured.records[0].getMessage(), "Test info logging message")

    def test_level(self):
        if "pydevd" in sys.modules or "pdb" in sys.modules:
            level = "DEBUG"
        else:
            level = "INFO"
        configure_logging()
        self.assertEqual(getattr(logging, level), logging.root.level)

        os.environ["OQAPI_LOG_LEVEL"] = "DEBUG"
        configure_logging()
        self.assertEqual(getattr(logging, "DEBUG"), logging.root.level)


if __name__ == "__main__":
    unittest.main()
