import unittest
from unittest.mock import MagicMock

from ohsome_quality_analyst import cli_opts


class TestCliOpts(unittest.TestCase):
    def test_int_or_str_param_type(self):
        param_type = cli_opts.IntOrStrParamType()
        param = MagicMock()
        ctx = MagicMock()
        self.assertIsInstance(param_type.convert(1, param, ctx), int)
        self.assertIsInstance(param_type.convert("One", param, ctx), str)
        with self.assertRaises(TypeError):
            self.assertIsInstance(param_type.convert(None, param, ctx), int)
