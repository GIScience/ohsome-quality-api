import os
import unittest
from types import MappingProxyType
from unittest import mock

from ohsome_quality_analyst import config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.keys = {
            "postgres_host",
            "postgres_port",
            "postgres_db",
            "postgres_user",
            "postgres_password",
            "data_dir",
            "geom_size_limit",
            "log_level",
            "ohsome_api",
            "concurrent_computations",
            "user_agent",
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

    @mock.patch.dict("os.environ", {"OQT_CONFIG": "/some/absolute/path"}, clear=True)
    def test_get_config_path_set_env(self):
        self.assertEqual(config.get_config_path(), "/some/absolute/path")

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_config_default(self):
        cfg = config.load_config_default()
        self.assertIsInstance(cfg, dict)
        self.assertEqual(self.keys, cfg.keys())

    @mock.patch.dict(
        "os.environ",
        {
            "OQT_CONFIG": os.path.join(
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
        {"OQT_GEOM_SIZE_LIMIT": "200", "POSTGRES_HOST": "foo"},
        clear=True,
    )
    def test_load_config_from_env_set(self):
        cfg = config.load_config_from_env()
        self.assertTrue(set(cfg.keys()).issubset(set(self.keys)))
        self.assertDictEqual(
            cfg,
            {"geom_size_limit": "200", "postgres_host": "foo"},
        )

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_config(self):
        cfg = config.get_config()
        self.assertIsInstance(cfg, MappingProxyType)
        self.assertEqual(self.keys, cfg.keys())

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_config_value(self):
        for key in self.keys:
            val = config.get_config_value(key)
            assert isinstance(val, int) or isinstance(val, str) or isinstance(val, dict)

    @mock.patch.dict(
        "os.environ",
        {"OQT_CONFIG": ""},
        clear=True,
    )
    def test_get_config_env_empty_str(self):
        cfg = config.get_config()
        self.assertIsInstance(cfg, MappingProxyType)
        self.assertEqual(self.keys, cfg.keys())

    @mock.patch.dict("os.environ", {}, clear=True)
    def test_get_data_dir_unset_env(self):
        data_dir = config.get_default_data_dir()
        expected = os.path.join(
            os.path.dirname(
                os.path.abspath(__file__),
            ),
            "..",
            "..",
            "data",
        )
        self.assertTrue(os.path.samefile(data_dir, expected))
