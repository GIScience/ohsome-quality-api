import unittest

import geojson

import ohsome_quality_analyst.utils.helper as helper


class TestHelper(unittest.TestCase):
    def setUp(self):
        pass

    def test_validate_geojson(self):
        gjson = """
            {"geometries":
                [{"coordinates": [[-115.81, 37.24]], "type": "MultiPoint"}],
            "type": "GeometryCollection"}
        """
        gjson_i = """
            {"geometries":
                [{"coordinates": [[37.24]], "type": "MultiPoint"}],
            "type": "GeometryCollection"}
        """

        obj = geojson.loads(gjson)
        assert helper.validate_geojson(gjson) is True
        assert helper.validate_geojson(obj) is True
        assert helper.validate_geojson(gjson_i) is False


if __name__ == "__main__":
    unittest.main()
