import asyncio
import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

import geojson
import httpx
import pytest
from geojson import FeatureCollection
from schema import Schema, SchemaError

from ohsome_quality_api.attributes.definitions import build_attribute_filter
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.utils.exceptions import OhsomeApiError

from .utils import get_geojson_fixture, get_topic_fixture


class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class TestOhsomeClientQuery(TestCase):
    def setUp(self) -> None:
        fixtures_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fixtures"
        )
        fixture = os.path.join(fixtures_dir, "ohsome-response-200-invalid.geojson")
        with open(fixture, "r") as reader:
            self.invalid_response_geojson = reader.read()
        fixture = os.path.join(fixtures_dir, "ohsome-response-200-valid.geojson")
        with open(fixture, "r") as reader:
            self.valid_response = reader.read()
        fixture = os.path.join(fixtures_dir, "ohsome-response-400-time.json")
        with open(fixture, "r") as reader:
            self.invalid_response_time = reader.read()

        self.ohsome_api = "https://api.ohsome.org/v1"
        self.bpolys = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        self.topic = get_topic_fixture("building-count")

    def test_valid_response(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.valid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            response = asyncio.run(ohsome_client.query(self.topic, self.bpolys))
            self.assertDictEqual(response, geojson.loads(self.valid_response))

    def test_invalid_response_with_status_code_200(self) -> None:
        """When response is streamed it can be invalid while status code equals 200"""
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.invalid_response_geojson,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            with self.assertRaises(OhsomeApiError):
                asyncio.run(ohsome_client.query(self.topic, self.bpolys))

    def test_status_code_400(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                400,
                content=self.invalid_response_time,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            with self.assertRaises(OhsomeApiError):
                asyncio.run(ohsome_client.query(self.topic, self.bpolys))

    def test_user_agent(self) -> None:
        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = httpx.Response(
                200,
                content=self.valid_response,
                request=httpx.Request("POST", "https://www.example.org/"),
            )
            asyncio.run(ohsome_client.query(self.topic, self.bpolys))
            self.assertEqual(
                "ohsome-quality-api",
                mock_request.call_args[1]["headers"]["user-agent"].split("/")[0],
            )


class TestOhsomeClientBuildUrl(TestCase):
    def setUp(self) -> None:
        self.ohsome_api = "https://api.ohsome.org/v1"
        self.topic = get_topic_fixture("building-count")
        self.attribute_filter = build_attribute_filter("height", self.topic.key)

    def test(self) -> None:
        ohsome_api = self.ohsome_api
        url = ohsome_client.build_url(self.topic)
        self.assertEqual(ohsome_api + "/elements/count", url)

    def test_group_by(self) -> None:
        url = ohsome_client.build_url(self.topic, group_by_boundary=True)
        self.assertEqual(self.ohsome_api + "/elements/count/groupBy/boundary", url)

    def test_ratio_false(self) -> None:
        ohsome_api = self.ohsome_api
        url = ohsome_client.build_url(self.topic)
        assert ohsome_api + "/elements/count" == url

    def test_ratio_true(self) -> None:
        ohsome_api = self.ohsome_api
        url = ohsome_client.build_url(self.topic, self.attribute_filter)
        assert ohsome_api + "/elements/count/ratio" == url

    def test_ratio_group_by(self) -> None:
        url = ohsome_client.build_url(
            self.topic, self.attribute_filter, group_by_boundary=True
        )
        assert self.ohsome_api + "/elements/count/ratio/groupBy/boundary" == url


class TestOhsomeClientBuildData(TestCase):
    def setUp(self) -> None:
        self.ohsome_api = "https://api.ohsome.org/v1"
        self.bpolys = get_geojson_fixture("heidelberg-altstadt-feature.geojson")
        self.topic = get_topic_fixture("building-count")
        self.attribute_filter = build_attribute_filter("height", self.topic.key)

    def test_feature(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
            }
        )
        data = ohsome_client.build_data_dict(self.topic, self.bpolys)
        self.assertTrue(schema.is_valid(data))

    def test_feature_collection(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
            }
        )
        bpolys = FeatureCollection([self.bpolys])
        data = ohsome_client.build_data_dict(self.topic, bpolys)
        self.assertTrue(schema.is_valid(data))

    def test_geometry(self) -> None:
        bpolys = self.bpolys.geometry
        with self.assertRaises(TypeError):
            ohsome_client.build_data_dict(self.topic, bpolys)

    def test_time(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                "time": str,
            }
        )
        data = ohsome_client.build_data_dict(self.topic, self.bpolys, time="2014-01-01")
        self.assertTrue(schema.is_valid(data))

    def test_ratio(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                "filter2": str,
            }
        )

        data = ohsome_client.build_data_dict(
            self.topic, self.bpolys, attribute_filter=self.attribute_filter
        )
        assert schema.is_valid(data) is True

    def test_ratio_time(self) -> None:
        schema = Schema(
            {
                "bpolys": str,
                "filter": str,
                "filter2": str,
                "time": str,
            }
        )
        data = ohsome_client.build_data_dict(
            self.topic,
            self.bpolys,
            time="2014-01-01",
            attribute_filter=self.attribute_filter,
        )
        assert schema.is_valid(data) is True


class TestOhsomeClientValidateQuery(TestCase):
    def setUp(self) -> None:
        self.ohsome_api = "https://api.ohsome.org/v1/"
        self.attribute_filter = build_attribute_filter("height", "building-count")

    def test_valid_1(self):
        data = {"result": [{"value": 1.0, "timestamp": "2020-03-20T01:30:08.180856"}]}
        self.assertDictEqual(data, ohsome_client.validate_query_results(data))

    def test_valid_2(self):
        data = {
            "result": [
                {
                    "value": 1.0,
                    "fromTimestamp": "2020-03-20T01:30:08.180856",
                    "toTimestamp": "2020-04-20T01:30:08.180856",
                }
            ]
        }
        self.assertDictEqual(data, ohsome_client.validate_query_results(data))

    def test_invalid_empty(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({})

    def test_invalid_empty_list(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({"result": []})

    def test_invalid_missing_key_timestamp(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({"result": [{"value": 1.0}]})

    def test_invalid_missing_key_value(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results(
                {"result": [{"timestamp": "2020-03-20T01:30:08.180856"}]}
            )

    def test_valid_group_by(self):
        data = {
            "groupByResult": [
                {
                    "result": [{"timestamp": "2018-01-01T00:00:00Z", "value": 23225.0}],
                    "groupByObject": "remainder",
                },
                {
                    "result": [{"timestamp": "2018-01-01T00:00:00Z", "value": 1418.0}],
                    "groupByObject": "building:roof",
                },
                {
                    "result": [{"timestamp": "2018-01-01T00:00:00Z", "value": 1178.0}],
                    "groupByObject": "building:roof:colour",
                },
            ]
        }
        self.assertDictEqual(
            data, ohsome_client.validate_query_results(data, group_by_boundary=True)
        )

    def test_invalid_empty_group_by(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results({}, group_by_boundary=True)

    def test_invalid_empty_list_group_by(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results(
                {"groupByResult": []}, group_by_boundary=True
            )

    def test_invalid_missing_key_group_by(self):
        with self.assertRaises(SchemaError):
            ohsome_client.validate_query_results(
                {
                    "groupByResult": [
                        {
                            "result": [
                                {
                                    "value": 1.0,
                                    "timestamp": "2020-03-20T01:30:08.180856",
                                }
                            ]
                        }
                    ]
                },
                group_by_boundary=True,
            )

    def test_valid_ratio(self):
        data = {
            "ratioResult": [
                {
                    "ratio": 1.0,
                    "value": 1.0,
                    "value2": 1.0,
                    "timestamp": "2020-03-20T01:30:08.180856",
                }
            ]
        }
        assert data == ohsome_client.validate_query_results(
            data,
            attribute_filter=self.attribute_filter,
        )

    def test_valid_ratio_nan(self):
        data = {
            "ratioResult": [
                {
                    "ratio": "NaN",
                    "value": 1.0,
                    "value2": 1.0,
                    "timestamp": "2020-03-20T01:30:08.180856",
                }
            ]
        }
        assert data == ohsome_client.validate_query_results(
            data, attribute_filter=self.attribute_filter
        )

    def test_invalid_empty_ratio(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {}, attribute_filter=self.attribute_filter
            )

    def test_invalid_empty_list_ratio(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {"ratioResult": []}, attribute_filter=self.attribute_filter
            )

    def test_invalid_missing_key_timestamp_ratio(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {"ratioResult": [{"value": 1.0}]},
                attribute_filter=self.attribute_filter,
            )

    def test_invalid_missing_key_value_ratio(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {"result": [{"timestamp": "2020-03-20T01:30:08.180856"}]},
                attribute_filter=self.attribute_filter,
            )

    def test_valid_ratio_group_by(self):
        data = {
            "groupByResult": [
                {
                    "ratioResult": [
                        {
                            "ratio": 1.0,
                            "value": 1.0,
                            "value2": 1.0,
                            "timestamp": "2020-03-20T01:30:08.180856",
                        }
                    ],
                    "groupByObject": "foo",
                }
            ]
        }
        assert data == ohsome_client.validate_query_results(
            data,
            attribute_filter=self.attribute_filter,
            group_by_boundary=True,
        )

    def test_invalid_empty_ratio_group_by(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {}, attribute_filter=self.attribute_filter, group_by_boundary=True
            )

    def test_invalid_empty_list_ratio_group_by(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {"groupByResult": []},
                attribute_filter=self.attribute_filter,
                group_by_boundary=True,
            )

    def test_invalid_missing_key_ratio_group_by(self):
        with pytest.raises(SchemaError):
            ohsome_client.validate_query_results(
                {
                    "groupByResult": [
                        {
                            "ratioResult": [
                                {
                                    "value": 1.0,
                                    "timestamp": "2020-03-20T01:30:08.180856",
                                }
                            ]
                        }
                    ]
                },
                attribute_filter=self.attribute_filter,
                group_by_boundary=True,
            )
