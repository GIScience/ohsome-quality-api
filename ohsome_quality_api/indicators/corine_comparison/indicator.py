from indicators.base import BaseIndicator


class CorineComparison(BaseIndicator):
    pass

    def preprocess(self) -> None:
        self.areas = []
        self.clc_classes_corine = []
        self.clc_classes_osm = []

    def calculate(self) -> None:
        pass

    def create_figure(self) -> None:
        pass
