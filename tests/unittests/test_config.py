import os
import unittest
from types import MappingProxyType
from unittest import mock

from ohsome_quality_api import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.keys = {
            "postgres_host",
            "postgres_port",
            "postgres_db",
            "postgres_user",
            "postgres_password",
            "ohsome_api_url",
            "heigit_api_key",
            "user_agent",
            "root_path",
            "docs_url",
            "log_level",
            "concurrent_computations",
            "datasets",
        }

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_config_path_empty_env(self):
        self.assertEqual(
            config.get_config_path(),
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "config",
                    "config.yaml",
                )
            ),
        )

    @mock.patch.dict("os.environ", {"OQAPI_CONFIG": "/some/absolute/path"}, clear=True)
    def test_get_config_path_set_env(self):
        self.assertEqual(config.get_config_path(), "/some/absolute/path")

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_config_default(self):
        cfg = config.load_config_default()
        self.assertIsInstance(cfg, dict)
        self.assertEqual(list(self.keys).sort(), list(cfg.keys()).sort())

    @mock.patch.dict(
        "os.environ",
        {
            "OQAPI_CONFIG": os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "fixtures",
                "config.yaml",
            )
        },
        clear=True,
    )
    def test_load_config_from_file(self):
        path = config.get_config_path()
        cfg = config.load_config_from_file(path)
        self.assertIsInstance(cfg, dict)
        self.assertTrue(cfg)  # Check if empty
        self.assertTrue(set(cfg.keys()).issubset(self.keys))

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_load_config_from_env_empty(self):
        cfg = config.load_config_from_env()
        self.assertTrue(set(cfg.keys()).issubset(set(self.keys)))
        self.assertEqual(cfg, {})

    @mock.patch.dict(
        "os.environ",
        {"POSTGRES_HOST": "foo"},
        clear=True,
    )
    def test_load_config_from_env_set(self):
        cfg = config.load_config_from_env()
        self.assertTrue(set(cfg.keys()).issubset(set(self.keys)))
        self.assertDictEqual(
            cfg,
            {"postgres_host": "foo"},
        )

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_config(self):
        cfg = config.get_config()
        self.assertIsInstance(cfg, MappingProxyType)
        self.assertEqual(list(self.keys).sort(), list(cfg.keys()).sort())

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_config_value(self):
        for key in self.keys:
            val = config.get_config_value(key)
            assert isinstance(val, (int, str, dict)) or val is None

    @mock.patch.dict(
        "os.environ",
        {"OQAPI_CONFIG": ""},
        clear=True,
    )
    def test_get_config_env_empty_str(self):
        cfg = config.get_config()
        self.assertIsInstance(cfg, MappingProxyType)
        self.assertEqual(list(self.keys).sort(), list(cfg.keys()).sort())
