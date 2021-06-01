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
from typing import Dict, List, Union

import asyncpg
import geojson
from asyncpg.exceptions import DataError, UndefinedColumnError


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


async def save_indicator_results(
    indicator, dataset: str, feature_id: Union[str, int]
) -> None:
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
        str(feature_id),
        indicator.result.timestamp_oqt,
        indicator.result.timestamp_osm,
        indicator.result.label,
        indicator.result.value,
        indicator.result.description,
        indicator.result.svg,
    )

    async with get_connection() as conn:
        await conn.execute(create_query)
        await conn.execute(upsert_query, *data)


async def load_indicator_results(
    indicator, dataset: str, feature_id: Union[str, int]
) -> bool:
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

    data = (
        indicator.metadata.name,
        indicator.layer.name,
        dataset,
        str(feature_id),
    )

    async with get_connection() as conn:
        query_result = await conn.fetchrow(query, *data)

    if not query_result:
        return False
    else:
        indicator.result.timestamp_oqt = query_result["timestamp_oqt"]
        indicator.result.timestamp_osm = query_result["timestamp_osm"]
        indicator.result.label = query_result["label"]
        indicator.result.value = query_result["value"]
        indicator.result.description = query_result["description"]
        indicator.result.svg = query_result["svg"]
        return True


async def get_feature_ids(dataset: str, fid_field: str) -> List[Union[int, str]]:
    """Get all ids of a certain dataset"""
    # Safe against SQL injection because of predefined values
    query = "SELECT {fid_field} FROM {dataset}".format(
        fid_field=fid_field, dataset=dataset
    )
    async with get_connection() as conn:
        records = await conn.fetch(query)
    return [record[fid_field] for record in records]


# TODO Rewrite to work with geojson.Feature as input
async def get_area_of_bpolys(bpolys: Dict):
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
    geom = json.dumps(bpolys["features"][0]["geometry"])
    async with get_connection() as conn:
        result = await conn.fetchrow(query, geom)
    return result["area_sqkm"]


async def get_bpolys_from_db(
    dataset: str, feature_id: Union[int, str], fid_field: str
) -> geojson.FeatureCollection:
    """Get bounding polygon from the Geodatabase as a GeoJSON Feature Collection."""
    logging.info("(dataset, fid_field, id): " + str((dataset, fid_field, feature_id)))

    # Safe against SQL injection because of predefined values
    # (See oqt.py and definitions.py)
    query = (
        """
        SELECT json_build_object(
            'type', 'FeatureCollection',
            'crs',  json_build_object(
                'type',      'name',
                'properties', json_build_object(
                    'name', 'EPSG:4326'
                )
            ),
            'features', json_agg(
                json_build_object(
                    'type',       'Feature',
                    'id',         {fid_field},
                    'geometry',   public.ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                    )
                )
            )
        )
        FROM {dataset}
        WHERE {fid_field} = $1
    """
    ).format(fid_field=fid_field, dataset=dataset)

    async with get_connection() as conn:
        try:
            result = await conn.fetchrow(query, feature_id)
        except (UndefinedColumnError, DataError):
            # TODO: Do we need a custom error here?
            # DataError occurs if feature id is a wrong type. E.g. str not int
            raise
    return geojson.loads(result[0])


async def get_available_regions() -> geojson.FeatureCollection:
    working_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(working_dir, "regions_as_geojson.sql")
    with open(file_path, "r") as file:
        query = file.read()
    async with get_connection() as conn:
        record = await conn.fetchrow(query)
    feature_collection = geojson.loads(record[0])
    # To be complaint with rfc7946 "id" should be a member of Feature not of Properties
    for feature in feature_collection["features"]:
        feature["id"] = feature["properties"].pop("id")
    return feature_collection
