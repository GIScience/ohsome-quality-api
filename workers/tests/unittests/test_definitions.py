import unittest

from ohsome_quality_analyst.utils.definitions import get_indicator_names


class TestDefinitions(unittest.TestCase):
    def test_get_indicator_names(self):
        names = get_indicator_names()
        self.assertIsInstance(names, list)
