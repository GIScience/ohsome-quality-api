import unittest

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.api import empty_api_response


class TestApi(unittest.TestCase):
    def test_empty_api_response(self):
        with self.assertRaises(TypeError):
            empty_api_response()

        response_template = {
            "apiVersion": oqt_version,
            "attribution": {
                "text": "© OpenStreetMap contributors",
                "url": "https://ohsome.org/copyrights",
            },
            "requestUrl": "http://www.example.org/",
        }
        self.assertEqual(
            response_template, empty_api_response("http://www.example.org/")
        )
