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
from typing import List, Union

import asyncpg
import geojson
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

from ohsome_quality_analyst.utils.definitions import DATASETS
from ohsome_quality_analyst.utils.helper import (
    datetime_to_isostring_timestamp,
    unflatten_dict,
)


@asynccontextmanager
async def get_connection():
    host = os.getenv("POSTGRES_HOST", default="localhost")
    port = os.getenv("POSTGRES_PORT", default=5445)
    database = os.getenv("POSTGRES_DB", default="oqt")
    user = os.getenv("POSTGRES_USER", default="oqt")
    password = os.getenv("POSTGRES_PASSWORD", default="oqt")
    # DNS in libpq connection URI format
    dns = f"postgres://{user}:{password}@{host}:{port}/{database}"
    conn = await asyncpg.connect(dns)
    try:
        yield conn
    finally:
        await conn.close()


async def save_indicator_results(indicator, dataset: str, feature_id: str) -> None:
    """Save the indicator result for a given dataset and feature in the Geodatabase.

    Create results table if not exists.
    Insert or on conflict update results.
    """

    logging.info("Save indicator result to database")

    working_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(working_dir, "create_results_table.sql")
    with open(file_path, "r") as file:
        create_query = file.read()

    working_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(working_dir, "save_results.sql")
    with open(file_path, "r") as file:
        upsert_query = file.read()

    data = (
        indicator.metadata.name,
        indicator.layer.name,
        dataset,
        feature_id,
        indicator.result.timestamp_oqt,
        indicator.result.timestamp_osm,
        indicator.result.label,
        indicator.result.value,
        indicator.result.description,
        indicator.result.svg,
        json.dumps(indicator.as_feature(), default=datetime_to_isostring_timestamp),
    )

    async with get_connection() as conn:
        await conn.execute(create_query)
        await conn.execute(upsert_query, *data)


async def load_indicator_results(indicator, dataset: str, feature_id: str) -> bool:
    """Get the indicator result from the Geodatabase.

    Reads given dataset and feature id from the indicator object.
    Load indicators results from the Geodatabase.
    Writes retrieved results to the result attribute of the indicator object.
    """
    logging.info("Load indicator results from database")

    working_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(working_dir, "load_results.sql")
    with open(file_path, "r") as file:
        query = file.read()

    query_data = (
        indicator.metadata.name,
        indicator.layer.name,
        dataset,
        feature_id,
    )

    async with get_connection() as conn:
        query_result = await conn.fetchrow(query, *query_data)

    if not query_result:
        return False

    indicator.result.timestamp_oqt = query_result["timestamp_oqt"]
    indicator.result.timestamp_osm = query_result["timestamp_osm"]
    indicator.result.label = query_result["result_label"]
    indicator.result.value = query_result["result_value"]
    indicator.result.description = query_result["result_description"]
    indicator.result.svg = query_result["result_svg"]

    feature = geojson.loads(query_result["feature"])
    properties = unflatten_dict(feature["properties"])
    result_data = properties["data"]

    for key, value in result_data.items():
        setattr(indicator, key, value)
    return True


async def get_feature_ids(dataset: str) -> List[str]:
    """Get all ids of a certain dataset"""
    # Safe against SQL injection because of predefined values
    fid_field = DATASETS[dataset]["default"]
    query = "SELECT {fid_field} FROM {dataset}".format(
        fid_field=fid_field, dataset=dataset
    )
    async with get_connection() as conn:
        records = await conn.fetch(query)
    return [str(record[fid_field]) for record in records]


async def get_area_of_bpolys(bpolys: Union[Polygon, MultiPolygon]):
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
    fid_field = DATASETS[dataset]["default"]

    logging.info("Dataset name:     " + dataset)
    logging.info("Feature id:       " + feature_id)
    logging.info("Feature id field: " + fid_field)

    query = (
        "SELECT ST_AsGeoJSON(geom) "
        + "FROM {0} ".format(dataset)
        + "WHERE {0} = $1".format(fid_field)
    )
    logging.debug("SQL Query: " + query)
    if await type_of(dataset, fid_field) == "integer":
        feature_id = int(feature_id)
    async with get_connection() as conn:
        result = await conn.fetchrow(query, feature_id)
    return Feature(geometry=geojson.loads(result[0]))


async def get_regions_as_geojson() -> FeatureCollection:
    working_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(working_dir, "regions_as_geojson.sql")
    with open(file_path, "r") as file:
        query = file.read()
    async with get_connection() as conn:
        record = await conn.fetchrow(query)
    feature_collection = geojson.loads(record[0])
    # To be complaint with rfc7946 "id" should be a member of the feature
    # and not of the properties.
    for feature in feature_collection["features"]:
        feature["id"] = feature["properties"].pop("id")
    return feature_collection


async def get_regions():
    ids = await get_feature_ids("regions")
    result = []
    for id in ids:
        query = "SELECT  name, ogc_fid FROM regions WHERE ogc_fid = {}".format(id)
        async with get_connection() as conn:
            record = await conn.fetchrow(query)
        tupel = (record[0], record[1])
        result.append(tupel)
    return result


def sanity_check_dataset(dataset: str) -> bool:
    """Compare against pre-definied values to prevent SQL injection"""
    return dataset in DATASETS.keys()


def sanity_check_fid_field(dataset: str, fid_field: str) -> bool:
    """Compare against pre-definied values to prevent SQL injection"""
    return (
        fid_field in DATASETS[dataset]["other"]
        or fid_field == DATASETS[dataset]["default"]
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
    uid = DATASETS[dataset]["default"]
    query = (
        "SELECT {uid} ".format(uid=uid)
        + "FROM {dataset} ".format(dataset=dataset)
        + "WHERE {fid_field} = $1".format(fid_field=fid_field)
    )
    if await type_of(dataset, fid_field) == "integer":
        feature_id = int(feature_id)
    async with get_connection() as conn:
        record = await conn.fetchrow(query, feature_id)
    return str(record[0])
