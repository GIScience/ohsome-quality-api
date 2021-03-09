import json
import logging
from typing import Dict

from geojson import FeatureCollection
from ohsome_quality_analyst.geodatabase.auth import POSTGRES_SCHEMA, PostgresDB
from psycopg2 import sql


def get_table_name(dataset: str, indicator_name: str, layer_name: str) -> str:
    """Compose table name from dataset and indicator.

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


def get_table_constraint_name(
    dataset: str, indicator_name: str, layer_name: str
) -> str:
    """Compose table constraint name from dataset and indicator.

    The results table constraint is composed of names for dataset and indicator
    e.g. "subnational_boundaries_building_completeness_pkey".
    """
    return get_table_name(dataset, indicator_name, layer_name) + "_pkey"


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
    logging.info("Got bpolys geometry")
    return bpolys


def save_indicator_results(indicator) -> None:
    """Save the indicator result for the given dataset and feature in the geodatabase"""
    logging.info("Saving indicator result to database")
    db = PostgresDB()
    table = get_table_name(
        indicator.dataset, indicator.metadata.name, indicator.layer.name
    )
    table_constraint = get_table_constraint_name(
        indicator.dataset, indicator.metadata.name, indicator.layer.name
    )

    # TODO: double check table structure with ohsome-hex schema
    #   once we have a better understading of the structure
    #   of the indicator results we can add more columns here
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        CREATE TABLE IF NOT EXISTS {} (
          fid integer,
          label VARCHAR(20),
          value FLOAT,
          description VARCHAR(1024),
          svg  TEXT,
          CONSTRAINT {} PRIMARY KEY (fid)
        );
        INSERT INTO {} (fid, label, value, description, svg) VALUES
        (%(feature_id)s, %(label)s, %(value)s ,%(description)s, %(svg)s)
        ON CONFLICT (fid) DO UPDATE
            SET (label, value, description, svg)=
            (excluded.label, excluded.value, excluded.description, excluded.svg)
    """
    ).format(
        sql.Identifier(table),
        sql.Identifier(table_constraint),
        sql.Identifier(table),
    )

    data = {
        "schema": POSTGRES_SCHEMA,
        "feature_id": indicator.feature_id,
        "label": indicator.result.label,
        "value": indicator.result.value,
        "description": indicator.result.description,
        "svg": indicator.result.svg,
    }
    db.query(query=query, data=data)


def load_indicator_results(indicator) -> bool:
    """Get the indicator result from the geodatabase.

    Reads given dataset and feature_id from the indicator object.
    Load indicators results from the geodatabase.
    Writes retrived results to the result attribute of the indicator object.
    """

    table = get_table_name(
        indicator.dataset, indicator.metadata.name, indicator.layer.name
    )
    fields = ["label", "value", "description", "svg"]
    query_result = {}
    for field in fields:
        # TODO: maybe this can be put into a single query
        db = PostgresDB()
        query = sql.SQL(
            """
            SET SCHEMA %(schema)s;
            SELECT {}
            FROM {}
            WHERE fid = %(feature_id)s;
        """
        ).format(sql.Identifier(field), sql.Identifier(table))
        data = {"schema": POSTGRES_SCHEMA, "feature_id": indicator.feature_id}
        query_results = db.retr_query(query=query, data=data)
        if not query_results:
            return False
        results = query_results[0][0]
        query_result[field] = results

    logging.info("Got indicator results from database")
    indicator.result.label = query_result["label"]
    indicator.result.value = query_result["value"]
    indicator.result.description = query_result["description"]
    indicator.result.svg = query_result["svg"]
    return True


def create_dataset_table(dataset_name: str) -> None:
    """Creates dataset table with collums fid and geom"""
    db = PostgresDB()
    query = sql.SQL(
        """DROP TABLE IF EXISTS {};
        CREATE TABLE {} (
            fid integer NOT Null,
            geom geometry,
            PRIMARY KEY(fid)
        );"""
    ).format(*[sql.Identifier(dataset_name)] * 2)
    db.query(query)


def get_fid_list(dataset_name: str) -> list:
    """Get all feature ids of a certain dataset"""
    db = PostgresDB()
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT fid FROM {}
    """
    ).format(sql.Identifier(dataset_name))
    data = {"schema": POSTGRES_SCHEMA}
    fids = db.retr_query(query, data)
    return [i[0] for i in fids]


def get_zonal_stats_population(bpolys: Dict):
    """Derive zonal population stats for given GeoJSON geometry.

    This is based on the Global Human Settlement Layer Population.
    """

    db = PostgresDB()
    query = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT
        SUM(
            (public.ST_SummaryStats(
                public.ST_Clip(
                    rast,
                    st_setsrid(public.ST_GeomFromGeoJSON(%(polygon)s), 4326)
                )
            )
        ).sum) population
        ,public.ST_Area(
            st_setsrid(public.ST_GeomFromGeoJSON(%(polygon)s)::public.geography, 4326)
        ) / (1000*1000) as area_sqkm
        FROM ghs_pop
        WHERE
         public.ST_Intersects(
            rast,
            st_setsrid(public.ST_GeomFromGeoJSON(%(polygon)s), 4326)
         )
        """
    )
    # need to get geometry only
    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"schema": POSTGRES_SCHEMA, "polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    population, area = query_results[0]
    logging.info("Got population inside polygon")

    return population, area


def get_area_of_bpolys(bpolys: Dict):
    """Calculates the area of a geojson geometry in postgis"""

    db = PostgresDB()

    query = sql.SQL(
        """
        SELECT
            public.ST_Area(
                st_setsrid(
                    public.ST_GeomFromGeoJSON(%(polygon)s)::public.geography,
                    4326
                    )
            ) / (1000*1000) as area_sqkm
        """
    )

    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    area = query_results[0][0]

    logging.info("Got area of polygon")

    return area
