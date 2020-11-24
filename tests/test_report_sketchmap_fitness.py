import os
import unittest

from ohsome_quality_tool.oqt import get_dynamic_report
from ohsome_quality_tool.utils.definitions import Reports


class TestSketchmapFitnessReport(unittest.TestCase):
    def setUp(self):
        self.test_dir = os.path.dirname(os.path.abspath(__file__))
        self.report_name = Reports.SKETCHMAP_FITNESS.name

    def test_get_dynamic_report(self):
        """Test if dynamic report can be calculated."""
        infile = os.path.join(self.test_dir, "fixtures/heidelberg_altstadt.geojson")
        results = get_dynamic_report(report_name=self.report_name, infile=infile)

        # check if result dict contains the right keys
        self.assertListEqual(
            list(results.keys()), ["indicators", "quality_level", "description"]
        )


if __name__ == "__main__":
    unittest.main()
