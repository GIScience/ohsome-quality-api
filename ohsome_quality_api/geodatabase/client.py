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

import logging
import os
from contextlib import asynccontextmanager
from typing import Literal

import asyncpg
import geojson
from asyncpg import Pool, Record
from fastapi import FastAPI, Request
from geojson import Feature, FeatureCollection, MultiPolygon

from ohsome_quality_api.config import get_config_value

logger = logging.getLogger("ohsome_quality_api")

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


OQAPIDB_POOL: Pool
OHSOMEDB_POOL: Pool


def log_query(record):
    logger.debug("Query:\n" + record.query)
    logger.debug("Args:\n" + str(record.args))


@asynccontextmanager
async def create_pool_for_lifespan(app: FastAPI):
    # DSN in libpq connection URI format
    oqapidb_dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("postgres_host"),
        port=get_config_value("postgres_port"),
        database=get_config_value("postgres_db"),
        user=get_config_value("postgres_user"),
        password=get_config_value("postgres_password"),
    )
    ohsomedb_dsn = "postgres://{user}:{password}@{host}:{port}/{database}".format(
        host=get_config_value("ohsomedb_host"),
        port=get_config_value("ohsomedb_port"),
        database=get_config_value("ohsomedb_db"),
        user=get_config_value("ohsomedb_user"),
        password=get_config_value("ohsomedb_password"),
    )
    server_settings = {
        "application_name": get_config_value("user_agent"),
        "search_path": get_config_value("ohsomedb_search_path"),
    }
    async with (
        asyncpg.create_pool(oqapidb_dsn) as oqapidb_pool,
        asyncpg.create_pool(
            ohsomedb_dsn,
            min_size=5,  # TODO put into config value
            max_size=30,  # TODO put info config value
            server_settings=server_settings,
        ) as ohsomedb_pool,
    ):
        app.state.oqapidb_pool = await oqapidb_pool
        app.state.ohsomedb_pool = await ohsomedb_pool
        yield


def set_pool_for_request(request: Request):
    global OQAPIDB_POOL
    global OHSOMEDB_POOL
    OQAPIDB_POOL = request.app.state.oqapidb_pool
    OHSOMEDB_POOL = request.app.state.ohsomedb_pool
    yield


@asynccontextmanager
async def get_connection(database: Literal["oqapidb", "ohsomedb"] = "oqapidb"):
    global OQAPIDB_POOL
    global OHSOMEDB_POOL
    match database:
        case "oqapidb":
            pool = OQAPIDB_POOL
        case "ohsomedb":
            pool = OHSOMEDB_POOL
    async with pool.acquire() as conn:
        try:
            with conn.query_logger(log_query):
                yield conn
        finally:
            await conn.close()


async def fetch(
    query: str,
    *args,
    database: Literal["oqapidb", "ohsomedb"] = "oqapidb",
) -> list:
    async with get_connection(database) as conn:
        return await conn.fetch(query, *args)


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


# TODO: Check calls of the function
async def get_reference_coverage(table_name: str) -> Feature:
    """Get reference coverage for a bounding polygon."""
    file_path = os.path.join(WORKING_DIR, "select_coverage.sql")
    with open(file_path, "r") as file:
        query = file.read()
    async with get_connection() as conn:
        result = await conn.fetch(query.format(table_name=table_name))
    return Feature(geometry=geojson.loads(result[0]["geom"]))


async def get_intersection_area(bpoly: Feature, table_name: str) -> float:
    """Get ratio of AOI area to intersection area of AOI and coverage geometry.

    The result is the ratio of area within coverage (between 0-1) or an empty list if
    AOI lies outside of coverage geometry.
    """
    file_path = os.path.join(WORKING_DIR, "select_intersection.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        result = await conn.fetch(query.format(table_name=table_name), geom)
        if result:
            return result[0]["area_ratio"]
        else:
            return 0.0


async def get_intersection_geom(bpoly: Feature, table_name: str) -> Feature:
    """Get intersection geometry of AoI and coverage geometry."""
    file_path = os.path.join(WORKING_DIR, "select_intersection.sql")
    with open(file_path, "r") as file:
        query = file.read()
    geom = str(bpoly.geometry)
    async with get_connection() as conn:
        result = await conn.fetch(query.format(table_name=table_name), geom)
        if result:
            return Feature(geometry=geojson.loads(result[0]["geom"]))
        else:
            return Feature(geometry=MultiPolygon(coordinates=[]))
