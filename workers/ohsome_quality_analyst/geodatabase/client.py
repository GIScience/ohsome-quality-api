import json
from typing import Dict

from geojson import FeatureCollection
from psycopg2 import sql

from ohsome_quality_analyst.geodatabase.auth import POSTGRES_SCHEMA, PostgresDB
from ohsome_quality_analyst.utils.definitions import logger


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
    logger.info(f"got bpolys geometry from {dataset} for feature {feature_id}.")
    return bpolys


def save_indicator_results(indicator) -> None:
    """Save the indicator result for the given dataset and feature in the database.

    The results table is super simplistic. For now we only store the feature_id and
    the results as a json object.
    """

    db = PostgresDB()

    # the results table is composed of the initial dataset name and the indicator
    # e.g. "subnational_boundaries_building_completeness"
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
    logger.info(
        f"Saved '{indicator.metadata.name}' indicator result "
        f"for feature {indicator.feature_id} in {table}."
    )


def load_indicator_results(indicator) -> bool:
    """Get the indicator result from the geodatabase.

    Reads given dataset and feature_id from the indicator object.
    Writes retrived results to the result attribute of the indicator object.

    Returns:
        bool:   True for results retrived.
                False for no results retrived
                (feature_id does not exist in the result relation/table).
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

    logger.info(f"Got results for feature {indicator.feature_id} from {table}.")
    # TODO Rewrite to use Result class definied in BaseIndicator class
    indicator.result.label = query_result["label"]
    indicator.result.value = query_result["value"]
    indicator.result.description = query_result["description"]
    indicator.result.svg = query_result["svg"]
    return True


def create_dataset_table(dataset: str):
    """Creates dataset table with collums fid and geom"""
    db = PostgresDB()
    exe = sql.SQL(
        """DROP TABLE IF EXISTS {};
        CREATE TABLE {} (
            fid integer NOT Null,
            geom geometry,
            PRIMARY KEY(fid)
        );"""
    ).format(*[sql.Identifier(dataset)] * 2)
    db.query(exe)


def geojson_to_table(dataset: str, infile: str, fid_key="fid"):
    """creates a table and loads the content of a geojson file to it"""

    create_dataset_table(dataset)

    with open(infile) as inf:
        data = json.load(inf)

    db = PostgresDB()
    for feature in data["features"]:
        polygon = json.dumps(feature["geometry"])
        fid = feature["properties"][fid_key]
        exe = sql.SQL(
            """INSERT INTO {table} (fid, geom)
                          VALUES (%(fid)s , public.ST_GeomFromGeoJSON(%(polygon)s))
                          ON CONFLICT (fid) DO UPDATE
                          SET geom = excluded.geom;;"""
        ).format(table=sql.Identifier(dataset))
        db.query(exe, {"fid": fid, "polygon": polygon})


def get_error_table_name(dataset: str, indicator: str, layer_name: str):
    """returns the name of the Error Table for the given dataset and indicator"""

    return f"{dataset}_{indicator}_{layer_name}_errors"


def get_fid_list(table: str):
    """get all FIDs of a certain dataset

    Results are returned as list
    """
    db = PostgresDB()

    exe = sql.SQL(
        """
        SET SCHEMA %(schema)s;
        SELECT fid FROM {}
    """
    ).format(sql.Identifier(table))
    data = {"schema": POSTGRES_SCHEMA}
    fids = db.retr_query(exe, data)
    return [i[0] for i in fids]


def create_error_table(dataset: str, indicator: str, layer_name: str):
    """(Re)Creates an error table to handle exceptions during processing
    of indicators.
    """

    table = get_error_table_name(dataset, indicator, layer_name)

    db = PostgresDB()
    exe = sql.SQL(
        """
        DROP TABLE IF EXISTS {};
        CREATE TABLE {} (
            fid integer NOT Null,
            error VARCHAR(256),
            PRIMARY KEY(fid)
        );
    """
    ).format(*[sql.Identifier(table)] * 2)
    db.query(exe)


def insert_error(dataset: str, indicator: str, layer_name: str, fid: int, error: str):
    """handles exceptionsduring processing of indicators.
    Stores failed fid and error message
    """
    table = get_error_table_name(dataset, indicator, layer_name)
    db = PostgresDB()
    exe = sql.SQL(
        """
        INSERT INTO {}
        VALUES (%(fid)s , %(error)s)
    """
    ).format(sql.Identifier(table))
    db.query(exe, {"fid": fid, "error": str(error)})


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
                    public.ST_GeomFromGeoJSON(%(polygon)s)
                )
            )
        ).sum) population
        ,public.ST_Area(
            public.ST_GeomFromGeoJSON(%(polygon)s)::public.geography
        ) / (1000*1000) as area_sqkm
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
    population, area = query_results[0]
    logger.info("Got population for polygon.")

    return population, area


def get_zonal_stats_guf(bpolys: Dict):
    """Derive zonal built up area stats for given GeoJSON geometry.

    This is based on the Global Urban Footprint dataset.
    """
    db = PostgresDB()

    query = sql.SQL(
        """
    SET SCHEMA %(schema)s;
    SELECT
        SUM(ST_Area ((pixel_as_polygon).geom::geography))
            / (1000*1000) as build_up_area_sqkm,
        public.ST_Area(
                    public.ST_GeomFromGeoJSON(%(polygon)s)::public.geography
                ) / (1000*1000) as area_sqkm
    FROM (
        SELECT
            -- ST_PixelAsPolygons will exclude pixel with nodata values
            ST_PixelAsPolygons(
                ST_Clip(
                    rast, ST_GeomFromGeoJSON (%(polygon)s)
                )
            ) AS pixel_as_polygon
        FROM
            guf04_daressalaam
        WHERE
            ST_Intersects (rast, ST_GeomFromGeoJSON (%(polygon)s))
            -- Avoid following ERROR of rt_raster_from_two_rasters during ST_Clip:
            -- The two rasters provided do not have the same alignment
            AND ST_BandIsNoData (rast) = FALSE) AS foo;"""
    )

    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"schema": "public", "polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    built_up_area, area = query_results[0]

    logger.info("Got built up area for polygon.")

    return built_up_area, area


def get_area_of_bpolys(bpolys: Dict):
    """Calculates the area of a geojson geometry in postgis.

    Using the database here so that we do not need to rely on
    GDAL being installed for python.
    """

    db = PostgresDB()

    query = sql.SQL(
        """
        SELECT
            public.ST_Area(
                public.ST_GeomFromGeoJSON(%(polygon)s)::public.geography
            ) / (1000*1000) as area_sqkm
        """
    )

    polygon = json.dumps(bpolys["features"][0]["geometry"])
    data = {"polygon": polygon}
    query_results = db.retr_query(query=query, data=data)
    area = query_results[0][0]

    logger.info("Got area for polygon.")

    return area
