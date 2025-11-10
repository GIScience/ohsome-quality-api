"""Currentness Indicator

Abbreviations:
    contrib_rel: Relative number of contributions per month [%]
    contrib_abs: Absolute number of contributions per month [%]
    contrib_sum: Total number of contributions
    ts: Timestamp
    th: Threshold
"""

import json
import locale
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from string import Template

import plotly.graph_objects as pgo
import yaml
from babel.dates import format_date
from babel.numbers import format_decimal, format_percent
from dateutil.parser import isoparse
from fastapi_i18n import _, get_locale
from geojson import Feature
from ohsome_filter_to_sql.main import ohsome_filter_to_sql
from plotly.subplots import make_subplots

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.definitions import Color
from ohsome_quality_api.geodatabase import client
from ohsome_quality_api.indicators.base import BaseIndicator
from ohsome_quality_api.ohsome import client as ohsome_client
from ohsome_quality_api.topics.models import BaseTopic as Topic

# set locale for datetime to string formatting
try:
    locale.setlocale(locale.LC_ALL, ["en_US", locale.getencoding()])
except locale.Error:
    logging.warning(
        "Could not set locale to en_US. Output may be different than expected."
    )


@dataclass
class Bin:
    """Bin or bucket of contributions.

    Indices denote years since latest timestamp.
    """

    contrib_abs: list
    contrib_rel: list
    timestamps: list  # middle of time period


class Currentness(BaseIndicator):
    def __init__(
        self,
        topic: Topic,
        feature: Feature,
    ) -> None:
        super().__init__(topic=topic, feature=feature)
        # thresholds for binning in months
        self.up_to_date, self.out_of_date, self.th_source = load_thresholds(
            self.topic.key
        )
        # thresholds for determining result class based on share of features in bins
        self.contrib_sum = 0
        self.bin_total: Bin
        self.bin_up_to_date: Bin
        self.bin_in_between: Bin
        self.bin_out_of_date: Bin

    async def preprocess(self, ohsomedb: bool = False):
        if ohsomedb:
            await self.preprocess_ohsomedb()
        else:
            await self.preprocess_ohsomeapi()

    async def preprocess_ohsomeapi(self):
        """Fetch all latest contributions in monthly buckets since 2008

        Beside the creation, latest contribution includes also the change to the
        geometry and the tag. It excludes deletion.
        """
        latest_ohsome_stamp = await ohsome_client.get_latest_ohsome_timestamp()
        end = latest_ohsome_stamp.strftime("%Y-%m-01")
        start = "2008-" + latest_ohsome_stamp.strftime("%m-%d")
        interval = "{}/{}/{}".format(start, end, "P1M")  # YYYY-MM-DD/YYYY-MM-DD/P1Y
        response = await ohsome_client.query(
            self.topic,
            self.feature,
            time=interval,
            count_latest_contributions=True,
            contribution_type="geometryChange,creation,tagChange",  # exclude 'deletion'
        )
        timestamps = []
        contrib_abs = []
        contrib_sum = 0
        for c in reversed(response["result"]):  # latest contributions first
            timestamps.append(isoparse(c["toTimestamp"]))
            contrib_abs.append(c["value"])
            contrib_sum += c["value"]
        if contrib_sum == 0:
            contrib_rel = [0 for _ in contrib_abs]
        else:
            contrib_rel = [c / contrib_sum for c in contrib_abs]
        self.bin_total = Bin(
            contrib_abs,
            contrib_rel,
            timestamps,
        )
        self.contrib_sum = contrib_sum
        self.result.timestamp_osm = timestamps[0]

    async def preprocess_ohsomedb(self):
        where = ohsome_filter_to_sql(self.topic.filter)
        with open(Path(__file__).parent / "query.sql", "r") as file:
            template = file.read()

        match self.topic.aggregation_type:
            case "count":
                aggregation = "COUNT(*)"
            case "length":
                aggregation = """
        0.001 * SUM(
            CASE
                WHEN ST_Within(
                    c.geom,
                    ST_GeomFromGeoJSON($1)
                )
                THEN c.length -- Use precomputed area from ohsome-planet
                ELSE ST_Length(
                      ST_Intersection(
                        c.geom,
                        ST_GeomFromGeoJSON($1)
                      )::geography
                )
            END
        )::BIGINT
                """
            case "area" | r"area\density":
                aggregation = """
        0.001 * 0.001 * SUM(
            CASE
                WHEN ST_Within(
                    c.geom,
                    ST_GeomFromGeoJSON($1)
                )
                THEN c.area -- Use precomputed area from ohsome-planet
                ELSE ST_Area(
                      ST_Intersection(
                        c.geom,
                        ST_GeomFromGeoJSON($1)
                      )::geography
                )
            END
        )::BIGINT
                """
            case _:
                raise ValueError(
                    "Unknown aggregation_type: {aggregation_type}".format(
                        aggregation_type=self.topic.aggregation_type
                    )
                )

        query = Template(template).substitute(
            {
                "aggregation": aggregation,
                "filter": where,
                "contributions_table": get_config_value("ohsomedb_contributions_table"),
            }
        )
        results = await client.fetch(
            query,
            json.dumps(self.feature["geometry"]),
            database="ohsomedb",
        )
        if len(results) == 0:
            # no data
            self.contrib_sum = 0
            return
        timestamps = []
        contrib_abs = []
        contrib_sum = 0
        for r in reversed(results[0:]):  # latest contributions first
            timestamps.append(r[0])
            contrib_abs.append(r[1])
            contrib_sum += r[1]
        if contrib_sum == 0:
            contrib_rel = [0 for _ in contrib_abs]
        else:
            contrib_rel = [c / contrib_sum for c in contrib_abs]
        self.bin_total = Bin(
            contrib_abs,
            contrib_rel,
            timestamps,
        )
        self.contrib_sum = contrib_sum
        self.result.timestamp_osm = self.bin_total.timestamps[0]

    def calculate(self):
        """Determine up-to-date, in-between and out-of-date contributions.

        Put contributions into three bins: (1) up-to-date (2) in-between and (3)
        out-of-date. The range of those bins are based on the topic.
        After binning determine the result class based on share of features in each bin.
        """
        edge_cases = check_major_edge_cases(self.contrib_sum)
        if edge_cases:
            self.result.description = edge_cases
            return
        self.result.description = check_minor_edge_cases(
            self.contrib_sum,
            self.bin_total,
            self.topic.aggregation_type,
        )

        self.bin_up_to_date = create_bin(
            self.bin_total,
            0,
            self.up_to_date,
        )
        self.bin_in_between = create_bin(
            self.bin_total,
            self.up_to_date,
            self.out_of_date,
        )
        self.bin_out_of_date = create_bin(
            self.bin_total,
            self.out_of_date,
            -1,
        )

        self.result.value = sum(self.bin_up_to_date.contrib_rel)

        if sum(self.bin_out_of_date.contrib_rel) >= 0.3:  # [%]
            self.result.class_ = 1
        elif sum(self.bin_up_to_date.contrib_rel) >= 0.75:
            self.result.class_ = 5
        elif sum(self.bin_up_to_date.contrib_rel) >= 0.5:
            self.result.class_ = 4
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= 0.75
        ):
            self.result.class_ = 3
        elif (
            sum(self.bin_up_to_date.contrib_rel) + sum(self.bin_in_between.contrib_rel)
            >= 0.5
        ):
            self.result.class_ = 2
        else:
            self.result.class_ = 1

        match self.topic.aggregation_type:
            case "count":
                unit = ""
                aggregation = self.contrib_sum
            case "length":
                unit = " km"
                aggregation = f"{self.contrib_sum:.1f}"
            case "area":
                unit = " km<sup>2</sup>"
                aggregation = f"{self.contrib_sum:.1f}"

        label_description = getattr(self.templates.label_description, self.result.label)
        self.result.description += Template(
            self.templates.result_description
        ).substitute(
            up_to_date_contrib_rel=f"{
                format_percent(
                    round(sum(self.bin_up_to_date.contrib_rel), 4),
                    locale=get_locale(),
                )
            }",
            aggregation=int(aggregation),
            unit=unit,
            from_timestamp=format_date(
                self.bin_up_to_date.timestamps[-1],
                format="MMM yyyy",
                locale=get_locale(),
            ),
            to_timestamp=format_date(
                self.bin_up_to_date.timestamps[0],
                format="MMM yyyy",
                locale=get_locale(),
            ),
        )
        self.result.description += "\n" + label_description

    def create_figure(self):
        if self.result.label == "undefined":
            logging.info(_("Result is undefined. Skipping figure creation."))
            return

        match self.topic.aggregation_type:
            case "count":
                unit = ""
            case "length":
                unit = " km"
            case "area":
                unit = " km<sup>2</sup>"
            case _:
                ValueError()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        for bucket, color in zip(
            (self.bin_up_to_date, self.bin_in_between, self.bin_out_of_date),
            (Color.GREEN, Color.YELLOW, Color.RED),
        ):
            contrib_abs_text = [
                f"{format_decimal(round(c, 2), locale=get_locale())}{unit}"
                for c in bucket.contrib_abs
            ]
            contrib_rel_text = [
                f"{format_decimal(round(c * 100, 2), locale=get_locale())}%"
                for c in bucket.contrib_rel
            ]
            timestamps_text = [
                format_date(ts, format="MMM yyyy", locale=get_locale())
                for ts in bucket.timestamps
            ]
            customdata = list(zip(contrib_rel_text, contrib_abs_text, timestamps_text))
            hovertemplate = _(
                "%{customdata[0]} of features (%{customdata[1]}) "
                "were last modified in %{customdata[2]}"
                "<extra></extra>"
            )

            # mock trace for absolute contributions to get second y-axis
            fig.add_trace(
                pgo.Bar(
                    name=None,
                    x=bucket.timestamps,
                    y=bucket.contrib_abs,
                    marker_color=color.value,
                    showlegend=False,
                    hovertemplate=None,
                    hoverinfo="skip",
                    xperiod="M1",
                    xperiodalignment="middle",
                ),
                secondary_y=True,
            )
            # trace for relative contributions
            fig.add_trace(
                pgo.Bar(
                    name="{:.1%} {}".format(
                        sum(bucket.contrib_rel),
                        self.get_threshold_text(color),
                    ),
                    x=bucket.timestamps,
                    y=bucket.contrib_rel,
                    marker_color=color.value,
                    customdata=customdata,
                    hovertemplate=hovertemplate,
                    xperiod="M1",
                    xperiodalignment="middle",
                    xhoverformat="%b %Y",
                )
            )

        fig.update_layout(
            title_text=_("Currentness"),
            barmode="relative",
            hovermode="x unified",
        )
        fig.update_xaxes(
            title_text=_("Date of Last Edit"),
            type="date",
            ticklabelmode="period",
            tickformat="%b\n%Y",
            ticks="outside",
            tick0=self.bin_total.timestamps[-1],
        )
        fig.update_yaxes(
            title_text=_("Features [%]"),
            tickformatstops=[
                dict(dtickrange=[None, 0.001], value=".2%"),
                dict(dtickrange=[0.001, 0.01], value=".1%"),
                dict(dtickrange=[0.01, 0.1], value=".0%"),
                dict(dtickrange=[0.1, None], value=".0%"),
            ],
            secondary_y=False,
        )
        fig.update_yaxes(
            title_text=_("Features [#]"),
            tickformat=".",
            secondary_y=True,
            griddash="dash",
        )
        # fixed legend, because we do not expect high contributions in 2008
        fig.update_legends(
            title=_("Last Edit to a Feature{}").format(self.get_source_text()),
            x=0.02,
            y=0.95,
            bgcolor="rgba(255,255,255,0.66)",
        )

        raw = fig.to_dict()
        raw["layout"].pop("template")  # remove boilerplate
        self.result.figure = raw

    def get_threshold_text(self, color: Color) -> str:
        up_to_date_str = month_to_year_month(self.up_to_date)
        out_of_date_str = month_to_year_month(self.out_of_date)
        match color:
            case color.GREEN:
                return _("younger than {up_to_date_str}").format(
                    up_to_date_str=up_to_date_str
                )
            case color.YELLOW:
                return _("between {up_to_date_str} and {out_of_date_str}").format(
                    up_to_date_str=up_to_date_str, out_of_date_str=out_of_date_str
                )
            case color.RED:
                return _("older than {out_of_date_str}").format(
                    out_of_date_str=out_of_date_str
                )
            case _:
                raise ValueError()

    def get_source_text(self) -> str:
        if self.th_source != "":
            self.th_source = f"<a href='{self.th_source}' target='_blank'>*</a>"
        return self.th_source


def month_to_year_month(months: int):
    years, months = divmod(months, 12)
    years_str = months_str = ""
    if years != 0:
        if years == 1:
            years_str = _("{years} year").format(years=years)
        else:
            years_str = _("{years} years").format(years=years)
    if months != 0:
        if months == 1:
            months_str = _("{months} month").format(months=months)
        else:
            months_str = _("{months} months").format(months=months)
    return " ".join([years_str, months_str]).strip()


def load_thresholds(topic_key: str) -> tuple[int, int, str]:
    """Load thresholds based on topic keys.

    Thresholds denote the number of months since today.
    Thresholds are used to discern if the features are up-to-date or out-of-date.

    up-to-data: everything up to this number of months is considered up-to-date
    out-of-date: everything older than this number of months is considered out-of-date

    Returns:
        tuple: (up-to-date, out-of-date)
    """
    file = os.path.join(os.path.dirname(__file__), "thresholds.yaml")
    with open(file, "r") as f:
        raw = yaml.safe_load(f)
    try:
        # topic thresholds
        source = raw[topic_key].get("source", "")
        thresholds = raw[topic_key]["thresholds"]
        up_to_date, out_of_date = (thresholds["up_to_date"], thresholds["out_of_date"])
    except KeyError:
        # default thresholds
        return 36, 96, ""
    return up_to_date, out_of_date, source


def create_bin(b: Bin, i: int, j: int) -> Bin:
    return Bin(
        contrib_abs=b.contrib_abs[i:j],
        contrib_rel=b.contrib_rel[i:j],
        timestamps=b.timestamps[i:j],
    )


def check_major_edge_cases(contrib_sum) -> str:
    """Check edge cases and return description.

    Major edge cases should lead to cancellation of calculation.
    """
    if contrib_sum == 0:  # no data
        return _(
            "In the area of interest no features of the selected topic are present "
            "today."
        )
    else:
        return ""


def check_minor_edge_cases(contrib_sum, bin_total, aggregation_type) -> str:
    """Check edge cases and return description.

    Minor edge cases should *not* lead to cancellation of calculation.
    """
    num_months = get_num_months_last_contrib(bin_total.contrib_abs)
    if contrib_sum < 25 and aggregation_type == "count":  # not enough data
        return _(
            "Please note that in the area of interest less than 25 features of the "
            "selected topic are present today. "
        )
    elif num_months >= 12:
        return _(
            "Please note that there was no mapping activity for {num_months} months "
            "in this region. "
        ).format(num_months=num_months)
    else:
        return ""


def get_num_months_last_contrib(contrib: list) -> int:
    """Get the number of months since today when the last contribution has been made."""
    for month, contrib in enumerate(contrib):  # latest contribution first
        if contrib != 0:
            return month


def get_median_month(contrib_rel: list) -> int:
    """Get the number of months since today when 50% of contributions have been made."""
    contrib_rel_cum = 0
    for month, contrib in enumerate(contrib_rel):  # latest contribution first
        contrib_rel_cum += contrib
        if contrib_rel_cum >= 0.5:
            return month
