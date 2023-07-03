"""This module is an asynchronous client to the geodatabase.

The PostgreSQL driver used is asyncpg:
    https://magicstack.github.io/asyncpg/current/

On preventing SQL injections:
    asyncpg supports native PostgreSQL syntax for SQL parameter substitution.
    asyncpg does not support SQL identifiers substitution (e.g. names of tables/fields).

    SQL identifiers can not be passed to the execute method like SQL parameters.
    (This is unlike psycopg2 which has extensive query interpolation mechanisms.)

    If the query string is build from user input,
    please make sure no SQL injection attack is possible.
"""

import json
import logging
import os
from contextlib import asynccontextmanager

import asyncpg
import geojson
from asyncpg import Record
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

from ohsome_quality_analyst.config import get_config_value
from ohsome_quality_analyst.indicators.base import BaseIndicator as Indicator
from ohsome_quality_analyst.utils.exceptions import EmptyRecordError
from ohsome_quality_analyst.utils.helper import json_serialize

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


@asynccontextmanager
async def get_connection():
    # DNS in libpq connection URI format
    dns = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    conn = await asyncpg.connect(dns)
    try:
        yield conn
    finally:
        await conn.close()


async def save_indicator_results(
    indicator: Indicator,
    dataset: str,
    feature_id: str,
) -> None:
    """Save the indicator result for a given dataset and feature in the Geodatabase.

    Create results table if not exists.
    Insert or on conflict update results.
    """

    logging.info("Save indicator result to database")

    file_path = os.path.join(WORKING_DIR, "create_results_table.sql")
    with open(file_path) as file:
        create_query = file.read()

    file_path = os.path.join(WORKING_DIR, "save_results.sql")
    with open(file_path) as file:
        upsert_query = file.read()

    data = (
        indicator.metadata.name,
        indicator.topic.name,
        dataset,
        feature_id,
        indicator.result.timestamp_oqt,
        indicator.result.timestamp_osm,
        indicator.result.class_,
        indicator.result.value,
        indicator.result.description,
        indicator.result.svg,
        json.dumps(indicator.as_feature(include_data=True), default=json_serialize),
    )

    async with get_connection() as conn:
        await conn.execute(create_query)
        await conn.execute(upsert_query, *data)


async def load_indicator_results(
    indicator: Indicator,
    dataset: str,
    feature_id: str,
) -> Indicator:
    """Get the indicator result from the Geodatabase.

    Reads given dataset and feature id from the indicator object.
    Load indicators results from the Geodatabase.
    Writes retrieved results to the result attribute of the indicator object.

    Returns:
        Indicator object

    Raises:
        EmptyRecordError: If database query returns an empty record.
    """
    logging.info("Load Indicator results from database")

    file_path = os.path.join(WORKING_DIR, "load_results.sql")
    with open(file_path) as file:
        query = file.read()

    query_data = (
        indicator.metadata.name,
        indicator.topic.name,
        dataset,
        feature_id,
    )

    async with get_connection() as conn:
        query_result = await conn.fetchrow(query, *query_data)

    if not query_result:
        raise EmptyRecordError()

    indicator.result.timestamp_oqt = query_result["timestamp_oqt"]
    indicator.result.timestamp_osm = query_result["timestamp_osm"]
    indicator.result.class_ = query_result["result_class"]
    indicator.result.value = query_result["result_value"]
    indicator.result.description = query_result["result_description"]
    indicator.result.svg = query_result["result_svg"]

    # Write data back to the attributes of the indicator object
    feature = geojson.loads(query_result["feature"])
    if "data" in feature["properties"]:
        for key, value in feature["properties"]["data"].items():
            setattr(indicator, key, value)
    return indicator


async def get_feature_ids(dataset: str) -> list[str]:
    """Get all ids of a certain dataset"""
    # Safe against SQL injection because of predefined values
    fid_field = get_config_value("datasets")[dataset]["default"]
    query = "SELECT {fid_field} FROM {dataset}".format(
        fid_field=fid_field, dataset=dataset
    )
    async with get_connection() as conn:
        records = await conn.fetch(query)
    return [str(record[fid_field]) for record in records]


async def get_area_of_bpolys(bpolys: Polygon | MultiPolygon):
    """Calculates the area of a geojson geometry in postgis"""
    logging.info("Get area of polygon")
    query = """
        SELECT
            public.ST_Area(
                st_setsrid(
                    public.ST_GeomFromGeoJSON($1)::public.geography,
                    4326
                    )
            ) / (1000*1000) as area_sqkm
        """
    async with get_connection() as conn:
        result = await conn.fetchrow(query, geojson.dumps(bpolys))
    return result["area_sqkm"]


async def get_feature_from_db(dataset: str, feature_id: str) -> Feature:
    """Get regions from geodatabase as a GeoJSON Feature object"""
    if not sanity_check_dataset(dataset):
        raise ValueError("Input dataset is not valid: " + dataset)
    fid_field = get_config_value("datasets")[dataset]["default"]

    logging.info("Dataset name:     " + dataset)
    logging.info("Feature id:       " + feature_id)
    logging.info("Feature id field: " + fid_field)

    query = (
        "SELECT ST_AsGeoJSON(geom) " + f"FROM {dataset} " + f"WHERE {fid_field} = $1"
    )
    logging.debug("SQL Query: " + query)
    if await type_of(dataset, fid_field) == "integer":
        feature_id = int(feature_id)
    async with get_connection() as conn:
        result = await conn.fetchrow(query, feature_id)
    return Feature(geometry=geojson.loads(result[0]))


async def get_regions_as_geojson() -> FeatureCollection:
    file_path = os.path.join(WORKING_DIR, "regions_as_geojson.sql")
    with open(file_path) as file:
        query = file.read()
    async with get_connection() as conn:
        record = await conn.fetchrow(query)
    feature_collection = geojson.loads(record[0])
    # To be compliant with rfc7946 "id" should be a member of the feature
    # and not of the properties.
    for feature in feature_collection["features"]:
        feature["id"] = feature["properties"].pop("id")
    return feature_collection


async def get_regions() -> list[dict]:
    query = "SELECT  name, ogc_fid FROM regions"
    async with get_connection() as conn:
        records = await conn.fetch(query)
    return [dict(r) for r in records]


def sanity_check_dataset(dataset: str) -> bool:
    """Compare against pre-defined values to prevent SQL injection"""
    return dataset in get_config_value("datasets").keys()


def sanity_check_fid_field(dataset: str, fid_field: str) -> bool:
    """Compare against pre-defined values to prevent SQL injection"""
    return (
        fid_field in get_config_value("datasets")[dataset]["other"]
        or fid_field == get_config_value("datasets")[dataset]["default"]
    )


async def type_of(table_name: str, column_name: str) -> str:
    """Get data type of field"""
    query = (
        "SELECT data_type "
        + "FROM information_schema.columns "
        + "WHERE table_name = $1 AND column_name = $2"
    )
    async with get_connection() as conn:
        record = await conn.fetchrow(query, table_name, column_name)
    return record[0]


async def map_fid_to_uid(dataset: str, feature_id: str, fid_field: str) -> str:
    """Map feature id to the unique feature id of the dataset"""
    if not sanity_check_dataset(dataset):
        raise ValueError("Input dataset is not valid: " + dataset)
    if not sanity_check_fid_field(dataset, fid_field):
        raise ValueError("Input feature id field is not valid: " + fid_field)
    uid = get_config_value("datasets")[dataset]["default"]
    query = f"SELECT {uid} " + f"FROM {dataset} " + f"WHERE {fid_field} = $1"
    if await type_of(dataset, fid_field) == "integer":
        feature_id = int(feature_id)
    async with get_connection() as conn:
        record = await conn.fetchrow(query, feature_id)
    return str(record[0])


async def get_shdi(bpoly: Feature | FeatureCollection) -> list[Record]:
    """Get Subnational Human Development Index (SHDI) for a bounding polygon.

    Get SHDI by intersecting the bounding polygon with sub-national regions provided by
    the GlobalDataLab (GDL).

    If intersection with multiple GDL regions occurs, return the weighted average using
    the intersection area as the weight.
    """
    file_path = os.path.join(WORKING_DIR, "select_shdi.sql")
    with open(file_path) as file:
        query = file.read()
    if isinstance(bpoly, Feature):
        geom = [str(bpoly.geometry)]
    elif isinstance(bpoly, FeatureCollection):
        geom = [str(feature.geometry) for feature in bpoly.features]
    else:
        raise TypeError(
            "Expected type `Feature` or `FeatureCollection`. Got `{}` instead.".format(
                type(bpoly)
            )
        )
    async with get_connection() as conn:
        return await conn.fetch(query, geom)
