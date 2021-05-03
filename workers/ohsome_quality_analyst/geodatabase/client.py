"""This module implements a asynchronous client to the geodatabase.

The PostgreSQL driver used is asyncpg.

On preventing SQL injections:
    asyncpg supports native PostgreSQL syntax for SQL parameter substitution.
    asyncpg does not support SQL identifiers (e.g. names tables/fields) substitution.

    SQL identifiers can not be passed to the execute method like SQL parameters.
    (This is unlike psycopg2 which has extensive query interpolation mechanisms.)

    If the query string is build from user input check,
    please make sure no SQL injection attack is possible.
"""

import json
import logging
import os
import pathlib
from contextlib import asynccontextmanager
from typing import Dict, List

import asyncpg
import geojson


def _get_table_name(dataset: str, indicator_name: str, layer_name: str) -> str:
    """Compose result table name from dataset and indicator.

    The results table is composed of names for dataset and indicator
    e.g. "subnational_boundaries_building_completeness".
    """
    indicator_name = indicator_name.replace(" ", "_")
    indicator_name = indicator_name.replace("-", "_")
    indicator_name = indicator_name.lower()
    layer_name = layer_name.replace(" ", "_")
    layer_name = layer_name.replace("-", "_")
    layer_name = layer_name.lower()
    return f"{dataset}_{indicator_name}_{layer_name}"


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


async def save_indicator_results(indicator, dataset, feature_id) -> None:
    """Save the indicator result for the given dataset and feature in the geodatabase"""
    logging.info("Save indicator result to database")
    table_name = _get_table_name(dataset, indicator.metadata.name, indicator.layer.name)
    table_pkey = table_name + "_pkey"
    # Safe against SQL injection because of predefined values
    create_query = (
        """
            CREATE TABLE IF NOT EXISTS {0} (
              fid INTEGER,
              timestamp_oqt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
              timestamp_osm TIMESTAMP WITH TIME ZONE,
              label VARCHAR(20),
              value FLOAT,
              description VARCHAR(1024),
              svg  TEXT,
              CONSTRAINT {1} PRIMARY KEY (fid)
            )
            """
    ).format(table_name, table_pkey)
    # Safe against SQL injection because of predefined values
    upsert_query = (
        """
            INSERT INTO {0} (
                fid,
                timestamp_oqt,
                timestamp_osm,
                label,
                value,
                description,
                svg)
            VALUES (
                $1,
                $2,
                $3,
                $4,
                $5,
                $6,
                $7)
            ON CONFLICT (fid)
                DO UPDATE SET
                    (
                        timestamp_oqt,
                        timestamp_osm,
                        label,
                        value,
                        description,
                        svg) = (
                        excluded.timestamp_oqt,
                        excluded.timestamp_osm,
                        excluded.label,
                        excluded.value,
                        excluded.description,
                        excluded.svg)
            """
    ).format(table_name)
    data = (
        feature_id,
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


async def load_indicator_results(indicator, dataset, feature_id) -> bool:
    """Get the indicator result from the geodatabase.

    Reads given dataset and feature_id from the indicator object.
    Load indicators results from the geodatabase.
    Writes retrived results to the result attribute of the indicator object.
    """
    logging.info("Load indicator results from database")
    table_name = _get_table_name(dataset, indicator.metadata.name, indicator.layer.name)
    query = (
        """
            SELECT
                timestamp_oqt,
                timestamp_osm,
                label,
                value,
                description,
                svg
            FROM {0}
            WHERE fid = $1
        """
    ).format(
        table_name
    )  # Safe against SQL injection because of predefined values

    async with get_connection() as conn:
        query_result = await conn.fetchrow(query, feature_id)
    if not query_result:
        return False

    indicator.result.timestamp_oqt = query_result["timestamp_oqt"]
    indicator.result.timestamp_osm = query_result["timestamp_osm"]
    indicator.result.label = query_result["label"]
    indicator.result.value = query_result["value"]
    indicator.result.description = query_result["description"]
    indicator.result.svg = query_result["svg"]
    return True


async def get_fids(dataset_name) -> List[int]:
    """Get all feature ids of a certain dataset"""
    # TODO: Does this apply for all datasets?
    # This works for test regions but does this work for GADM or HEX Cells?
    # Safe against SQL injection because of predefined values
    query = "SELECT ogc_fid FROM {0}".format(dataset_name)
    async with get_connection() as conn:
        records = await conn.fetch(query)
    return [record["ogc_fid"] for record in records]


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
    polygon = json.dumps(bpolys["features"][0]["geometry"])
    async with get_connection() as conn:
        result = await conn.fetchrow(query, polygon)
    return result["area_sqkm"]


async def get_bpolys_from_db(
    dataset: str, feature_id: int
) -> geojson.FeatureCollection:
    """Get geometry and properties from geo database as a geojson feature collection."""
    logging.info("Get bpolys geometry")
    # TODO: adjust this for other input tables
    # Safe against SQL injection because of predefined values
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
                    'id',         ogc_fid,
                    'geometry',   public.ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        -- list of fields
                        'fid', ogc_fid
                    )
                )
            )
        )
        FROM {0}
        WHERE ogc_fid = $1
    """
    ).format(dataset)
    async with get_connection() as conn:
        result = await conn.fetchrow(query, feature_id)
    return geojson.loads(result[0])


async def get_available_regions() -> geojson.FeatureCollection:
    wd = pathlib.Path(__file__).parent.absolute()
    fp = wd / "regions_as_geojson.sql"
    with open(fp, "r") as f:
        query = f.read()
    async with get_connection() as conn:
        record = await conn.fetchrow(query)
    feature_collection = geojson.loads(record[0])
    # To be complaint with rfc7946 "id" should be a member of Feature
    for feature in feature_collection["features"]:
        feature["id"] = feature["properties"].pop("id")
    return feature_collection


async def get_hex_ids(bpolys: dict, zoomLevel: int = 12) -> List[int]:
    """Get overlapping hexIDs for a bpoly from the db."""
    logging.info("Get corresponding hexIDs")
    query = """
            select geohash_id from public.isea3h_world_res_{}_hex
            where public.ST_Intersects(
                public.ST_Transform(public.st_setsrid(
                public.ST_GeomFromGeoJSON($1), 4326), 3857), geom) = True
        """.format(
        zoomLevel
    )
    bpolys = json.dumps(bpolys["features"][0]["geometry"])
    logging.info(bpolys)
    async with get_connection() as conn:
        result = await conn.fetch(query, bpolys)
    result = [x[0] for x in result]
    return result
