from ohsome_quality_tool.base.indicator import BaseIndicator


class Indicator(BaseIndicator):
    """The Building Completeness Indicator."""

    def __init__(self):
        self.name = "Building Completeness"
        self.min = 0
        self.max = 1

    def preprocess(self):
        print(f"run preprocessing for {self.name} indicator")

    def calculate(self):
        print(f"run calculation for {self.name} indicator")
