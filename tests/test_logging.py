import unittest

from ohsome_quality_tool.utils.definitions import logger


class TestLogging(unittest.TestCase):
    def test_logging(self):
        with self.assertLogs("oqt", level="INFO") as cm:
            logger.info("info")
            logger.error("error")
            self.assertEqual(cm.output, ["INFO:oqt:info", "ERROR:oqt:error"])


if __name__ == "__main__":
    unittest.main()
