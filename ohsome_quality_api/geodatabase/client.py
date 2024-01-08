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
import os
from contextlib import asynccontextmanager

import asyncpg
import geojson
from asyncpg import Record
from geojson import Feature, FeatureCollection

from ohsome_quality_api.config import get_config_value

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


async def get_shdi(bpoly: Feature | FeatureCollection) -> list[Record]:
    """Get Subnational Human Development Index (SHDI) for a bounding polygon.

    Get SHDI by intersecting the bounding polygon with sub-national regions provided by
    the GlobalDataLab (GDL).

    If intersection with multiple GDL regions occurs, return the weighted average using
    the intersection area as the weight.
    """
    file_path = os.path.join(WORKING_DIR, "select_shdi.sql")
    with open(file_path, "r") as file:
        query = file.read()
    if isinstance(bpoly, Feature):
        geom = [str(bpoly.geometry)]
    elif isinstance(bpoly, FeatureCollection):
        geom = [str(feature.geometry) for feature in bpoly.features]
    else:
        raise TypeError(
            "Expected type `Feature` or `FeatureCollection`. Got `{0}` instead.".format(
                type(bpoly)
            )
        )
    async with get_connection() as conn:
        return await conn.fetch(query, geom)


async def get_building_area(bpoly: Feature) -> list[Record]:
    """Get area of building footprints for a bounding polygon."""
    file_path = os.path.join(WORKING_DIR, "select_building_area.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        return await conn.fetch(query, geom)


async def get_building_area_mbf(bpoly: Feature) -> list[Record]:
    """Get area of building footprints for a bounding polygon."""
    file_path = os.path.join(WORKING_DIR, "mbf.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        return await conn.fetch(query, geom)


async def get_eubucco_coverage(inverse: bool) -> list[Record]:
    file_path = os.path.join(WORKING_DIR, "select_eubucco_coverage.sql")
    with open(file_path, "r") as file:
        query = file.read()
    if inverse:
        table_name = "eubucco_v0_1_coverage_inversed"
    else:
        table_name = "eubucco_v0_1_coverage_simple"
    query = query.format(table_name=table_name)
    async with get_connection() as conn:
        return await conn.fetch(query)


async def get_eubucco_coverage_intersection_area(bpoly: Feature) -> list[Record]:
    """Get ratio of AOI area to intersection area of AOI and coverage geometry.

    The result is the ratio of area within coverage (between 0-1) or an empty list if
    AOI lies outside of coverage geometry.
    """
    file_path = os.path.join(WORKING_DIR, "select_check_eubucco_coverage.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        return await conn.fetch(query, geom)


async def get_eubucco_coverage_intersection(bpoly: Feature) -> Feature:
    """Get intersection geometry of AoI and coverage geometry."""
    file_path = os.path.join(WORKING_DIR, "get_coverage_intersection.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        result = await conn.fetch(query, geom)
        bpoly["geometry"] = geojson.loads(result[0]["geom"])
        return bpoly
