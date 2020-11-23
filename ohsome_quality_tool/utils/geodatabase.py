import json
from typing import Dict

from geojson import FeatureCollection
from psycopg2 import sql

from ohsome_quality_tool.utils.auth import PostgresDB
from ohsome_quality_tool.utils.config import POSTGRES_SCHEMA
from ohsome_quality_tool.utils.definitions import logger


def get_table_name(dataset: str, indicator: str) -> str:
    """Compose table name from dataset and indicator.

    The results table is composed of names for dataset and indicator
    e.g. "subnational_boundaries_building_completeness".
    """

    return f"{dataset}_{indicator}"


def get_table_constraint_name(dataset: str, indicator: str) -> str:
    """Compose table constraint name from dataset and indicator.

    The results table constraint is composed of names for dataset and indicator
    e.g. "subnational_boundaries_building_completeness_pkey".
    """

    return f"{dataset}_{indicator}_pkey"


def get_bpolys_from_db(dataset: str, feature_id: int) -> FeatureCollection:
    """Get geometry and properties from geo database as a geojson feature collection."""

    db = PostgresDB()

    # TODO: adjust this for other input tables
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
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
        FROM {}
        WHERE fid = %(feature_id)s
    """
    ).format(sql.Identifier(dataset))
    data = {"schema": POSTGRES_SCHEMA, "feature_id": feature_id}
    query_results = db.retr_query(query=query, data=data)
    bpolys = query_results[0][0]
    logger.info(f"got bpolys geometry from {dataset} for feature {feature_id}.")
    return bpolys


def save_indicator_results_to_db(
    dataset: str, feature_id: int, indicator: str, results: Dict
) -> None:
    """Save the indicator result for the given dataset and feature in the database.

    The results table is super simplistic. For now we only store the feature_id and
    the results as a json object.
    """

    db = PostgresDB()

    # the results table is composed of the initial dataset name and the indicator
    # e.g. "subnational_boundaries_building_completeness"
    table = get_table_name(dataset, indicator)
    table_constraint = get_table_constraint_name(dataset, indicator)

    # TODO: double check table structure with ohsome-hex schema
    #   once we have a better understading of the structure
    #   of the indicator results we can add more columns here
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        CREATE TABLE IF NOT EXISTS {} (
          fid integer,
          results json,
          CONSTRAINT {} PRIMARY KEY (fid)
        );
        INSERT INTO {} (fid, results) VALUES
        (%(feature_id)s, %(results)s)
        ON CONFLICT (fid) DO UPDATE
            SET results = excluded.results;
    """
    ).format(
        sql.Identifier(table),
        sql.Identifier(table_constraint),
        sql.Identifier(table),
    )
    data = {
        "schema": POSTGRES_SCHEMA,
        "feature_id": feature_id,
        "results": json.dumps(results),
    }
    db.query(query=query, data=data)
    logger.info(f"Saved results for feature {feature_id} in {table}.")


def get_indicator_results_from_db(
    dataset: str, feature_id: int, indicator: str
) -> Dict:
    """Get the indicator result for the given dataset and feature in the database."""

    db = PostgresDB()
    table = get_table_name(dataset, indicator)
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT results
        FROM {}
        WHERE fid = %(feature_id)s;
    """
    ).format(sql.Identifier(table))
    data = {"schema": POSTGRES_SCHEMA, "feature_id": feature_id}
    query_results = db.retr_query(query=query, data=data)
    results = query_results[0][0]
    logger.info(f"Got results for feature {feature_id} from {table}.")
    return results


def get_value_from_db(dataset: str, feature_id: str, field_name: str):
    """Get the value for a field of the given dataset and feature in the database."""

    db = PostgresDB()
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT {}
        FROM {}
        WHERE fid = %(feature_id)s;
    """
    ).format(sql.Identifier(field_name), sql.Identifier(dataset))
    data = {"schema": POSTGRES_SCHEMA, "feature_id": feature_id}
    query_results = db.retr_query(query=query, data=data)
    results = query_results[0][0]
    logger.info(f"Got '{field_name}' for feature '{feature_id}' from '{dataset}'.")
    return results


def get_zonal_stats_population(bpolys: Dict):
    """Derive zonal population stats for given GeoJSON geometry.

    This is based on the Global Human Settlement Layer Population.
    """

    db = PostgresDB()
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT
        (public.ST_SummaryStats(
            public.ST_Union(
                public.ST_Clip(
                    rast,
                    public.ST_Transform(
                        public.ST_GeomFromGeoJSON(%(polygon)s)
                        , 954009)
                )
            )
        )).sum population
        FROM ghs_pop
        WHERE
         public.ST_Intersects(
            rast,
            public.ST_GeomFromGeoJSON(%(polygon)s)
         )
        """
    )
    # need to get geometry only
    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"schema": POSTGRES_SCHEMA, "polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    results = query_results[0][0]
    logger.info("Got population for polygon.")

    return results


def get_zonal_stats_guf(bpolys: Dict):
    """Derive zonal built up area stats for given GeoJSON geometry.

    This is based on the Global Urban Footprint dataset.
    """

    db = PostgresDB()
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT
        (public.ST_SummaryStats(
            public.ST_Union(
                public.ST_Clip(
                    rast,
                    public.ST_GeomFromGeoJSON(%(polygon)s)
                )
            )
        )).sum built_up_area
        FROM guf04
        WHERE
         public.ST_Intersects(
            rast,
            public.ST_GeomFromGeoJSON(%(polygon)s)
         )
        """
    )
    # need to get geometry only
    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"schema": POSTGRES_SCHEMA, "polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    results = query_results[0][0]
    logger.info("Got built up area for polygon.")

    return results
