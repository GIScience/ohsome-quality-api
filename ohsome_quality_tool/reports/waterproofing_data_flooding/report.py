from ohsome_quality_tool.base.report import BaseReport


class Report(BaseReport):
    """The Building Completeness Indicator."""

    def __init__(self):
        super().__init__()
        self.name = "Waterproofing Data Flooding"

    def calculate(self):
        print(f"derive report for {self.name}")
