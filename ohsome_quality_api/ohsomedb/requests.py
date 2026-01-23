from pathlib import Path
from typing import Literal

from geojson_pydantic.geometries import MultiPolygon, Polygon
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ohsome_filter_to_sql.main import OhsomeFilter, ohsome_filter_to_sql
from pydantic import validate_call

from ohsome_quality_api.config import get_config_value
from ohsome_quality_api.geodatabase import client

ENV = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    autoescape=select_autoescape(),
)


@validate_call
async def contributions(
    *,
    aggregation: Literal["count", "length", "area"],
    bpolys: Polygon | MultiPolygon,
    filter_: OhsomeFilter,
):
    sql_filter, sql_filter_args = ohsome_filter_to_sql(filter_)
    template = ENV.get_template("contributions.sql")
    query = template.render(
        **{
            "aggregation": aggregation,
            "contributions": get_config_value("ohsomedb_contributions_table"),
            "geom": len(sql_filter_args) + 1,
            "filter": sql_filter,
        }
    )
    return await client.fetch(
        query,
        *sql_filter_args,
        bpolys.model_dump_json(),
        database="ohsomedb",
    )


@validate_call
async def users(
    *,
    aggregation: Literal["count"] = "count",
    bpolys: Polygon | MultiPolygon,
    filter_: OhsomeFilter,
):
    sql_filter, sql_filter_args = ohsome_filter_to_sql(filter_)
    template = ENV.get_template("users.sql")
    query = template.render(
        **{
            # "aggregation": aggregation,
            "contributions": get_config_value("ohsomedb_contributions_table"),
            "geom": len(sql_filter_args) + 1,
            "filter": sql_filter,
        }
    )
    return await client.fetch(
        query,
        *sql_filter_args,
        bpolys.model_dump_json(),
        database="ohsomedb",
    )


@validate_call
async def elements(
    *,
    aggregation: Literal["count", "length", "area"],
    bpolys: Polygon | MultiPolygon,
    filter_: OhsomeFilter,
):
    sql_filter, sql_filter_args = ohsome_filter_to_sql(filter_)
    template = ENV.get_template("elements.sql")
    query = template.render(
        **{
            "aggregation": aggregation,
            "contributions": get_config_value("ohsomedb_contributions_table"),
            "geom": len(sql_filter_args) + 1,
            "filter": sql_filter,
        }
    )
    return await client.fetch(
        query,
        *sql_filter_args,
        bpolys.model_dump_json(),
        database="ohsomedb",
    )
