import logging
import os
from pathlib import Path

import geojson
import plotly.graph_objects as pgo
import yaml
from async_lru import alru_cache
from fastapi_i18n import _
from geojson import Feature
from numpy import mean

from ohsome_quality_api.definitions import Color, get_attribution
from ohsome_quality_api.geodatabase import client as db_client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic


class RoadComparison(BaseIndicator):
    """Comparison of OSM Roads with reference data.

    Result is a ratio of the length of reference roads wich are covered by OSM roads
    to the total length of reference roads.
    """

    def __init__(
        self,
        topic: BaseTopic,
        feature: Feature,
    ) -> None:
        super().__init__(
            topic=topic,
            feature=feature,
        )
        # TODO: Evaluate thresholds
        self.th_high = 0.85  # Above or equal to this value label should be green
        self.th_low = 0.50  # Above or equal to this value label should be yellow

        self.data_ref: dict[str, dict] = {}
        self.area_cov: dict[str, float | None] = {}
        self.length_matched: dict[str, float | None] = {}
        self.length_total: dict[str, float | None] = {}
        self.length_osm: dict[str, float | None] = {}
        self.ratio: dict[str, float | None] = {}
        self.warnings: dict[str, str | None] = {}
        # self.data_ref: list = load_reference_datasets()  # reference datasets
        for key, val in load_datasets_metadata().items():
            self.data_ref[key] = val
            self.area_cov[key] = None  # covered area [%]
            self.length_matched[key] = None
            self.length_total[key] = None
            self.length_osm[key] = None
            self.ratio[key] = None
            self.warnings[key] = None

    @classmethod
    async def coverage(cls, inverse=False) -> list[Feature]:
        # TODO: could also return a Feature Collection
        features = []
        datasets = load_datasets_metadata()
        for val in datasets.values():
            if inverse:
                table = val["coverage"]["inversed"]
            else:
                table = val["coverage"]["simple"]
            feature = await db_client.get_reference_coverage(table)
            feature.properties.update({"refernce_dataset": val["name"]})
            features.append(feature)
        return features

    @classmethod
    def attribution(cls) -> str:
        # TODO: add attribution
        return get_attribution(["OSM"])

    async def preprocess(self) -> None:
        for key, val in self.data_ref.items():
            # get area covered by reference dataset [%]
            self.area_cov[key] = await db_client.get_intersection_area(
                self.feature,
                val["coverage"]["simple"],
            )
            self.warnings[key] = self.check_major_edge_cases(key)
            if self.warnings[key] != "":
                continue

            # clip input geom with coverage of reference dataset
            feature = await db_client.get_intersection_geom(
                self.feature,
                val["coverage"]["simple"],
            )

            # get covered road length
            (
                self.length_matched[key],
                self.length_total[key],
            ) = await get_matched_roadlengths(
                geojson.dumps(feature),
                val["table_name"],
            )
            if self.length_total[key] is None:
                self.length_total[key] = 0
                self.length_matched[key] = 0
            elif self.length_matched[key] is None:
                self.length_matched[key] = 0

    def calculate(self) -> None:
        self.result.description = ""
        for key in self.data_ref.keys():
            # if major edge case present add to description
            # and continue with next dataset
            edge_case = self.check_major_edge_cases(key)
            if edge_case != "":
                self.result.description += edge_case + " "
                continue

            self.warnings[key] += self.check_minor_edge_cases(key)
            # ZeroDivisionError can not occur because of `check_major_edge_cases()`
            self.ratio[key] = self.length_matched[key] / self.length_total[key]

            self.result.description += self.warnings[key] + "\n"
            self.result.description += _(
                "{name} has a road length of "
                "{total_length} km, of which "
                "{matched_length}"
                " km are covered by roads in "
                "OSM. "
            ).format(
                name=self.data_ref[key]["name"],
                total_length=round(self.length_total[key] / 1000, 2),
                matched_length=round(self.length_matched[key] / 1000, 2),
            )

        ratios = [v for v in self.ratio.values() if v is not None]
        if ratios:
            self.result.value = float(mean(ratios))

        if self.result.value is not None:
            if self.result.value >= self.th_high:
                self.result.class_ = 5
            elif self.th_high > self.result.value >= self.th_low:
                self.result.class_ = 3
            elif self.th_low > self.result.value >= 0:
                self.result.class_ = 1

        label_description = getattr(self.templates.label_description, self.result.label)
        self.result.description += label_description
        # remove double white spaces
        self.result.description = " ".join(self.result.description.split())

    def create_figure(self) -> None:
        edge_cases = [self.check_major_edge_cases(k) for k in self.data_ref.keys()]
        if self.result.label == "undefined" and all(edge_cases):
            logging.info(
                "Result is undefined and major edge case is present."
                " Skipping figure creation."
            )
            return

        fig = pgo.Figure()

        ref_name = []
        ref_ratio = []
        ref_color = []
        ref_processingdate = []
        for key, val in self.ratio.items():
            if val is None:
                continue
            ref_name.append(self.data_ref[key]["name"])
            ref_color.append(Color[self.data_ref[key]["color"]].value)
            ref_processingdate.append(self.data_ref[key]["processing_date"])
            ref_ratio.append(val)

        for i, (name, ratio, date) in enumerate(
            zip(ref_name, ref_ratio, ref_processingdate)
        ):
            hovertext = _("OSM Covered: {length_matched} km ({date})").format(
                length_matched=round(self.length_matched[name] / 1000, 2),
                date=date.strftime("%b %d, %Y"),
            )
            fig.add_trace(
                pgo.Bar(
                    x=[name],
                    y=[ratio * 100],
                    name=_("{matched_percentage}% of {name} are matched by OSM").format(
                        matched_percentage=round((ratio * 100), 1), name=name
                    ),
                    marker=dict(
                        color=Color.GREY.value,
                        line=dict(color=Color.GREY.value, width=1),
                    ),
                    width=0.4,
                    hovertext=hovertext,
                    hoverinfo="text",
                )
            )
            length_difference_km = (
                self.length_total[name] - self.length_matched[name]
            ) / 1000
            fig.add_trace(
                pgo.Bar(
                    x=[name],
                    y=[100 - ratio * 100],
                    name=_(
                        "{not_matched_percentage}% of {name} are not matched by OSM"
                    ).format(
                        not_matched_percentage=round((100 - ratio * 100), 1), name=name
                    ),
                    marker=dict(
                        color="rgba(0,0,0,0)",
                        line=dict(color=Color.GREY.value, width=1),
                    ),
                    width=0.4,
                    hovertext=_(
                        "Not OSM Covered: {length_difference_km} km " + "({date})"
                    ).format(
                        length_difference_km=round(length_difference_km, 2),
                        date=date.strftime("%b %d, %Y"),
                    ),
                    hoverinfo="text",
                    textposition="outside",
                )
            )

        fig.update_layout(
            barmode="stack",
            title="Road Comparison",
            yaxis=dict(title=_("Matched road length [%]")),
        )

        fig.update_layout(
            legend=dict(
                orientation="h",
                entrywidth=270,
                yanchor="top",
                y=-0.1,
                xanchor="center",
                x=0.5,
            ),
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def check_major_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset] * 100
        if coverage is None or coverage == 0:
            return _(
                "Reference dataset {dataset} does not cover area-of-interest. "
            ).format(dataset=dataset)
        elif coverage < 10:
            return _(
                "Only {a}%% of the area-of-interest is covered "
                + "by the reference dataset ({b}). "
                + "No quality estimation with reference {c} is possible."
            ).format(a=round(coverage, 2), b=dataset, c=dataset)
        elif self.length_total[dataset] == 0:
            return _(
                "{dataset} does not contain roads for your area-of-interest. "
            ).format(dataset=dataset)
        else:
            return ""

    def check_minor_edge_cases(self, dataset: str) -> str:
        """If edge case is present return description if not return empty string."""
        coverage = self.area_cov[dataset] * 100
        if coverage < 95:
            return _(
                "{dataset} does only cover {coverage}% of your area-of-interest. "
                "Comparison is made for the intersection area."
            ).format(dataset=dataset, coverage=round(coverage, 2))
        else:
            return ""

    def format_sources(self):
        sources = []
        for dataset in self.data_ref.values():
            if dataset["link"] is not None:
                sources.append(f"<a href='{dataset['link']}'>{dataset['name']}</a>")
            else:
                sources.append(f"{dataset}")
        result = ", ".join(sources)
        return result


# alru needs hashable type, therefore, use string instead of Feature
@alru_cache
async def get_matched_roadlengths(
    feature_str: str,
    table_name: str,
) -> tuple[float, float]:
    file_path = Path(__file__).parent / "query.sql"
    with open(file_path, "r") as file:
        query = file.read()
    feature = geojson.loads(feature_str)
    table_name = table_name.replace(" ", "_")
    geom = geojson.dumps(feature.geometry)
    results = await db_client.fetch(
        query.format(table_name=table_name),
        geom,
    )
    return results[0][0], results[0][1]


def load_datasets_metadata() -> dict:
    file_path = os.path.join(os.path.dirname(__file__), "datasets.yaml")
    with open(file_path, "r") as f:
        return yaml.safe_load(f)
