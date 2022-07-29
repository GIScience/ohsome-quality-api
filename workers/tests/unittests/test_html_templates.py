import unittest

from jinja2 import Template

from ohsome_quality_analyst.html_templates import template


class TestHtmlTemplates(unittest.TestCase):
    def test_get_template_invalid_name(self):
        with self.assertRaises(ValueError):
            template.get_template("")
        with self.assertRaises(ValueError):
            template.get_template("foo")

    def test_get_template_indicator(self):
        self.assertIsInstance(template.get_template("indicator"), Template)

    def test_get_template_report(self):
        self.assertIsInstance(template.get_template("report"), Template)
