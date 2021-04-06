import json
import logging
import os
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
    create_query = (
        """
            CREATE TABLE IF NOT EXISTS {0} (
              fid integer,
              label VARCHAR(20),
              value FLOAT,
              description VARCHAR(1024),
              svg  TEXT,
              CONSTRAINT {1} PRIMARY KEY (fid)
            )
            """
    ).format(table_name, table_pkey)
    upsert_query = (
        """
            INSERT INTO {0} (fid, label, value, description, svg)
                VALUES ($1, $2, $3, $4 ,$5)
            ON CONFLICT (fid)
                DO UPDATE SET
                    (label, value, description, svg) = (excluded.label, excluded.value, excluded.description, excluded.svg)
            """  # noqa
    ).format(table_name)
    data = (
        feature_id,
        indicator.result.label,
        # TODO: Fix in indicator
        float(indicator.result.value),
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
            SELECT label, value, description, svg
            FROM {0}
            WHERE fid = $1
        """
    ).format(table_name)

    async with get_connection() as conn:
        query_result = await conn.fetchrow(query, feature_id)
    if not query_result:
        return False

    indicator.result.label = query_result["label"]
    indicator.result.value = query_result["value"]
    indicator.result.description = query_result["description"]
    indicator.result.svg = query_result["svg"]
    return True


async def get_fids(dataset_name) -> List[asyncpg.Record]:
    """Get all feature ids of a certain dataset"""
    query = "SELECT fid FROM {0}".format(dataset_name)
    async with get_connection() as conn:
        return await conn.fetch(query)


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
                    'id',         fid,
                    'geometry',   public.ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        -- list of fields
                        'fid', fid
                    )
                )
            )
        )
        FROM {0}
        WHERE fid = $1
    """
    ).format(dataset)
    async with get_connection() as conn:
        result = await conn.fetchrow(query, feature_id)
    return geojson.loads(result[0])
