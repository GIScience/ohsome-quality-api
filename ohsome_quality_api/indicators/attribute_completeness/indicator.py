import logging
import time
from string import Template

import plotly.graph_objects as go
import requests
from geojson import Feature
from shapely import to_wkt
from shapely.geometry import shape

from ohsome_quality_api.attributes.definitions import (
    build_attribute_filter,
    get_attribute,
)
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.topics.models import BaseTopic as Topic


class AttributeCompleteness(BaseIndicator):
    """
    Attribute completeness of map features.

    The ratio of features of a given topic to features of the same topic with additional
    (expected) attributes.

    Terminology:
        topic: Category of map features. Translates to a ohsome filter.
        attribute: Additional (expected) tag(s) describing a map feature.
            attribute_keys: a set of predefined attributes wich will be
                translated to an ohsome filter
            attribute_filter: ohsome filter query representing custom attributes
            attribute_title:  Title describing the attributes represented by
                the Attribute Filter

    Example: How many buildings (topic) have height information (attribute)?

    Premise: Every map feature of a given topic should have certain additional
        attributes.

    Limitation: Limited to one attribute.
    """

    # TODO make attribute a list
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
        attribute_keys: list[str] | None = None,
        attribute_filter: str | None = None,
        attribute_title: str | None = None,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        self.threshold_yellow = 0.75
        self.threshold_red = 0.25
        self.attribute_keys = attribute_keys
        self.attribute_filter = attribute_filter
        self.attribute_title = attribute_title
        self.absolute_value_1 = None
        self.absolute_value_2 = None
        self.description = None
        if self.attribute_keys:
            self.attribute_filter = build_attribute_filter(
                self.attribute_keys,
                self.topic.key,
            )
            self.attribute_title = ", ".join(
                [
                    get_attribute(self.topic.key, k).name.lower()
                    for k in self.attribute_keys
                ]
            )

    async def preprocess(self) -> None:

        TRINO_HOST = ""
        TRINO_PORT =
        TRINO_USER = ""
        TRINO_CATALOG = ""
        TRINO_SCHEMA = ""

        URL = f"http://{TRINO_HOST}:{TRINO_PORT}/v1/statement"

        HEADERS = {
            "X-Trino-User": TRINO_USER,
            "X-Trino-Catalog": TRINO_CATALOG,
            "X-Trino-Schema": TRINO_SCHEMA,
        }

        AUTH = None

        QUERY_TEMPLATE = """
SELECT
    SUM(
        CASE
            WHEN ST_Within(ST_GeometryFromText(a.geometry), b.geometry) THEN length
            ELSE CAST(st_length(ST_Intersection(ST_GeometryFromText(a.geometry), b.geometry)) AS integer)
        END
    ) AS total_road_length,
    
    SUM(
        CASE
            WHEN element_at(tags, 'name') IS NULL THEN 0
            WHEN ST_Within(ST_GeometryFromText(a.geometry), b.geometry) THEN length
            ELSE CAST(st_length(ST_Intersection(ST_GeometryFromText(a.geometry), b.geometry)) AS integer)
        END
    ) AS total_road_length_with_name,

    (
        SUM(
            CASE
                WHEN element_at(tags, 'name') IS NULL THEN 0
                WHEN ST_Within(ST_GeometryFromText(a.geometry), b.geometry) THEN length
                ELSE CAST(st_length(ST_Intersection(ST_GeometryFromText(a.geometry), b.geometry)) AS integer)
            END
        )
        /
        SUM(
            CASE
                WHEN ST_Within(ST_GeometryFromText(a.geometry), b.geometry) THEN length
                ELSE CAST(st_length(ST_Intersection(ST_GeometryFromText(a.geometry), b.geometry)) AS integer)
            END
        )
    ) AS ratio

FROM contributions a, (VALUES {aoi_values}) AS b(id, geometry)
WHERE 'herfort' != 'kwakye'
    AND status = 'latest'
    AND element_at(a.tags, 'highway') IS NOT NULL
    AND a.tags['highway'] IN (
        'motorway', 'trunk', 'motorway_link', 'trunk_link', 'primary', 'primary_link',
        'secondary', 'secondary_link', 'tertiary', 'tertiary_link', 'unclassified', 'residential'
    )
    AND (bbox.xmax >= 8.629761 AND bbox.xmin <= 8.742371)
    AND (bbox.ymax >= 49.379556 AND bbox.ymin <= 49.437890)
    AND ST_Intersects(ST_GeometryFromText(a.geometry), b.geometry)
GROUP BY b.id
        """

        def extract_geometry(feature):
            geometry = feature.get("geometry")
            if not geometry:
                raise ValueError("Feature does not contain a geometry")
            geom_shape = shape(geometry)
            return to_wkt(geom_shape)

        def format_aoi_values(geom_wkt):
            return f"('AOI', ST_GeometryFromText('{geom_wkt}'))"

        def execute_query(query):
            try:
                response = requests.post(URL, data=query, headers=HEADERS, auth=AUTH)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error submitting query: {e}")
                return None

        def poll_query(next_uri):
            """Poll the query's nextUri until results are ready."""
            results = []
            while next_uri:
                try:
                    response = requests.get(next_uri, headers=HEADERS, auth=AUTH)
                    response.raise_for_status()
                    data = response.json()

                    state = data["stats"]["state"]
                    print(f"Query state: {state}")

                    if state == "FINISHED":
                        if "data" in data:
                            results.extend(data["data"])
                        print("Query completed successfully!")
                        break
                    elif state in {"FAILED", "CANCELLED"}:
                        print(f"Query failed or was cancelled: {data}")
                        break

                    next_uri = data.get("nextUri")
                except requests.exceptions.RequestException as e:
                    print(f"Error polling query: {e}")
                    break
                time.sleep(1)

            return results


        geom_wkt = extract_geometry(self.feature)

        aoi_values = format_aoi_values(geom_wkt)

        query = QUERY_TEMPLATE.format(aoi_values=aoi_values)

        initial_response = execute_query(query)
        if not initial_response:
            return
        next_uri = initial_response.get("nextUri")
        if not next_uri:
            print("No nextUri found. Query might have failed immediately.")
            print(initial_response)
            return

        response = poll_query(next_uri)


        # timestamp = response["ratioResult"][0]["timestamp"]
        # self.result.timestamp_osm = dateutil.parser.isoparse(timestamp)
        self.absolute_value_1 = response[0][0]
        self.absolute_value_2 = response[0][1]
        self.result.value = self.absolute_value_2 / self.absolute_value_1

    def calculate(self) -> None:
        # result (ratio) can be NaN if no features matching filter1
        if self.result.value == "NaN":
            self.result.value = None
        if self.result.value is None:
            self.result.description += " No features in this region"
            return
        self.create_description()

        if self.result.value >= self.threshold_yellow:
            self.result.class_ = 5
            self.result.description = (
                self.description + self.templates.label_description["green"]
            )
        elif self.threshold_yellow > self.result.value >= self.threshold_red:
            self.result.class_ = 3
            self.result.description = (
                self.description + self.templates.label_description["yellow"]
            )
        else:
            self.result.class_ = 1
            self.result.description = (
                self.description + self.templates.label_description["red"]
            )

    def create_description(self):
        if self.result.value is None:
            raise TypeError("Result value should not be None.")
        else:
            result = round(self.result.value * 100, 1)
        if self.attribute_title is None:
            raise TypeError("Attribute title should not be None.")
        else:
            tags = "attributes " + self.attribute_title
        all, matched = self.compute_units_for_all_and_matched()
        self.description = Template(self.templates.result_description).substitute(
            result=result,
            all=all,
            matched=matched,
            topic=self.topic.name.lower(),
            tags=tags,
        )

    def create_figure(self) -> None:
        """Create a gauge chart.

        The gauge chart shows the percentage of features having the requested
        attribute(s).
        """
        if self.result.label == "undefined":
            logging.info("Result is undefined. Skipping figure creation.")
            return

        fig = go.Figure(
            go.Indicator(
                domain={"x": [0, 1], "y": [0, 1]},
                mode="gauge+number",
                value=self.result.value * 100,
                number={"suffix": "%"},
                type="indicator",
                gauge={
                    "axis": {
                        "range": [0, 100],
                        "tickwidth": 1,
                        "tickcolor": "darkblue",
                        "ticksuffix": "%",
                        "tickfont": dict(color="black", size=20),
                    },
                    "bar": {"color": "black"},
                    "steps": [
                        {"range": [0, self.threshold_red * 100], "color": "tomato"},
                        {
                            "range": [
                                self.threshold_red * 100,
                                self.threshold_yellow * 100,
                            ],
                            "color": "gold",
                        },
                        {
                            "range": [self.threshold_yellow * 100, 100],
                            "color": "darkseagreen",
                        },
                    ],
                },
            )
        )

        fig.update_layout(
            font={"color": "black", "family": "Arial"},
            xaxis={"showgrid": False, "range": [-1, 1], "fixedrange": True},
            yaxis={"showgrid": False, "range": [0, 1], "fixedrange": True},
            plot_bgcolor="rgba(0,0,0,0)",
            autosize=True,
        )

        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def compute_units_for_all_and_matched(self):
        if self.topic.aggregation_type == "count":
            all = f"{int(self.absolute_value_1)} elements"
            matched = f"{int(self.absolute_value_2)} elements"
        elif self.topic.aggregation_type == "area":
            all = f"{str(round(self.absolute_value_1, 2))} m²"
            matched = f"{str(round(self.absolute_value_2, 2))} m²"
        elif self.topic.aggregation_type == "length":
            all = f"{str(round(self.absolute_value_1, 2))} m"
            matched = f"{str(round(self.absolute_value_2, 2))} m"
        else:
            raise ValueError("Invalid aggregation_type")
        return all, matched
