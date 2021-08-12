import unittest

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst.api.api import empty_api_response


class TestApi(unittest.TestCase):
    def test_empty_api_response(self):
        response_template = {
            "apiVersion": oqt_version,
            "attribution": {
                "text": "© OpenStreetMap contributors",
                "url": "https://ohsome.org/copyrights",
            },
        }
        self.assertEqual(
            response_template, empty_api_response("https://www.example.org/")
        )
