import logging
import os
import sys
import unittest

from ohsome_quality_analyst.utils.definitions import configure_logging


class TestLogging(unittest.TestCase):
    def setUp(self):
        os.unsetenv("OQT_LOG_LEVEL")  # Unset variable for the use of this script

    def test_logging(self):
        configure_logging()
        with self.assertLogs(level="INFO") as captured:
            logging.info("Test logging message")
            logging.debug("Test logging message")
        # Test that there is only one log message
        self.assertEqual(len(captured.records), 1)
        # Test unformatted logging output message
        self.assertEqual(captured.records[0].getMessage(), "Test logging message")

    def test_level(self):
        if "pydevd" in sys.modules or "pdb" in sys.modules:
            level = "DEBUG"
        else:
            level = "INFO"
        configure_logging()
        self.assertEqual(getattr(logging, level), logging.root.level)

        os.environ["OQT_LOG_LEVEL"] = "DEBUG"
        configure_logging()
        self.assertEqual(getattr(logging, "DEBUG"), logging.root.level)


if __name__ == "__main__":
    unittest.main()
