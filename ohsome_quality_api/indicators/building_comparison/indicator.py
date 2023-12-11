import logging
from string import Template

import geojson
import plotly.express as px
import plotly.subplots as sp
from dateutil import parser
from geojson import Feature, MultiPolygon, Polygon
from numpy import mean

from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic


class BuildingComparison(BaseIndicator):
    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        self.area_osm: float | None = None
        self.area_references: dict = {}
        # The result is the ratio of area within coverage (between 0-1) or an empty list
        self.coverage: dict = {}

        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow
        self.above_one_th = 1.30

    @classmethod
    async def coverage(cls) -> Polygon | MultiPolygon:
        result = await db_client.get_eubucco_coverage()
        return geojson.loads(result[0]["geom"])

    @classmethod
    def attribution(cls) -> str:
        return get_attribution(["OSM", "EUBUCCO"])

    async def preprocess(self) -> None:
        result = await db_client.get_eubucco_coverage_intersection_area(self.feature)
        if result:
            self.coverage["EUBUCCO"] = result[0]["area_ratio"]
        else:
            self.coverage["EUBUCCO"] = None
            return
        if not self.check_major_edge_cases():
            self.feature = await db_client.get_eubucco_coverage_intersection(
                self.feature
            )
            db_query_result = await db_client.get_building_area(self.feature)
            raw = db_query_result[0]["area"] or 0
            self.area_references["EUBUCCO"] = raw / (1000 * 1000)

            osm_query_result = await ohsome_client.query(
                self.topic,
                self.feature,
            )
            raw = osm_query_result["result"][0]["value"] or 0  # if None
            self.area_osm = raw / (1000 * 1000)
            self.result.timestamp_osm = parser.isoparse(
                osm_query_result["result"][0]["timestamp"]
            )

    def calculate(self) -> None:
        # TODO: put checks into check_corner_cases. Let result be undefined.
        if not self.result.description == "":
            return
        if self.check_minor_edge_cases():
            self.result.description = self.check_minor_edge_cases()
        else:
            self.result.description = ""

        if all(v == 0 for v in self.area_references.values()):
            self.result.description += "Warning: No reference data in this area. "
            pass
        else:
            self.result.value = float(
                mean(
                    [self.area_osm / v for v in self.area_references.values() if v != 0]
                )
            )

        if self.result.value is None:
            return
        elif self.above_one_th >= self.result.value >= self.th_high:
            self.result.class_ = 5
        elif self.th_high > self.result.value >= self.th_low:
            self.result.class_ = 3
        elif self.th_low > self.result.value >= 0:
            self.result.class_ = 1
        elif self.result.value > self.above_one_th:
            self.result.description += (
                "Warning: No quality estimation made. "
                "OSM and reference data differ. Reference data is likely outdated. "
            )

        template = Template(self.metadata.result_description)
        self.result.description += template.substitute(
            ratio=round(self.result.value * 100, 2),
            coverage=round(self.coverage["EUBUCCO"] * 100, 2),
        )
        label_description = self.metadata.label_description[self.result.label]
        self.result.description += "\n" + label_description

    def create_figure(self) -> None:
        if self.result.label == "undefined" and self.check_major_edge_cases():
            logging.info(
                "Result is undefined and major edge case is present. "
                + "Skipping figure creation."
            )
            return

        fig = sp.make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Area", "Coverage"),
            specs=[[{"type": "xy"}, {"type": "mapbox"}]],
        )

        x_list = ["OSM"]
        y_list = [round(self.area_osm, 2)]
        for reference_set in ["EUBUCCO"]:
            x_list.append(reference_set)
            y_list.append(round(self.area_references[reference_set], 2))

        color_list = [Color.RED.value, Color.BLUE.value]

        trace1 = px.bar(
            x=x_list,
            y=y_list,
            color=x_list,
            color_discrete_sequence=color_list,
        )

        coords = self.feature["geometry"]["coordinates"]
        if self.feature["geometry"]["type"] == "Polygon":
            coords = [coords]
        lon = [
            innermost[0]
            for outermost in coords
            for inner in outermost
            for innermost in inner
        ]
        lat = [
            innermost[1]
            for outermost in coords
            for inner in outermost
            for innermost in inner
        ]
        trace2 = px.choropleth_mapbox(
            {"name": [self.feature["properties"]["name"]], "area": self.area_osm},
            geojson=self.feature,
            locations="name",
            featureidkey="properties.name",
            color=[self.coverage["EUBUCCO"]],
            color_continuous_scale="Viridis",
            range_color=(0, 1),
        )
        # Create a custom hover template
        hover_template = "<b>Name</b>: %{location}<br><b>EUBUCCO Coverage</b>: %{z}<br>"
        trace2.update_traces(hovertemplate=hover_template)

        #
        for trace, col in zip([trace1, trace2], range(1, 3)):
            for data in trace.data:
                fig.add_trace(data, row=1, col=col)

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_bounds={
                "west": min(lon) - 0.5,
                "east": max(lon) + 0.5,
                "south": min(lat) - 0.5,
                "north": max(lat) + 0.5,
            },
            showlegend=False,
            coloraxis=dict(showscale=False),
        )
        fig.update(
            layout_coloraxis_showscale=False,
        )
        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        for i in range(len(raw["data"])):
            if i < (len(raw["data"]) - 1):
                raw["data"][i]["x"] = raw["data"][i]["x"].tolist()
                raw["data"][i]["y"] = raw["data"][i]["y"].tolist()
            else:
                raw["data"][i]["z"] = raw["data"][i]["z"].tolist()
                raw["data"][i]["locations"] = raw["data"][i]["locations"].tolist()
        self.result.figure = raw

    def check_major_edge_cases(self) -> bool:
        coverage = self.coverage["EUBUCCO"]
        # TODO: generalize function
        if coverage is None or coverage == 0.00:
            self.result.description = (
                "Reference dataset does not cover area-of-interest."
            )
            return True
        elif coverage < 0.10:
            self.result.description = (
                "Only {:.2f}% of the area-of-interest is covered ".format(
                    coverage * 100
                )
                + "by the reference dataset (EUBUCCO). "
                + "No quality estimation is possible."
            )
            return True
        else:
            self.result.description = ""
            return False

    def check_minor_edge_cases(self) -> str:
        coverage = self.coverage["EUBUCCO"]
        if coverage < 0.95:
            return (
                "Warning: Reference data does not cover the whole input geometry. "
                + f"Input geometry is clipped to the coverage. Results is calculated"
                f" for {coverage}% of the input geometry."
            )
        else:
            return ""
