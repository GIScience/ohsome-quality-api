from geojson import FeatureCollection
from psycopg2 import sql

from ohsome_quality_tool.utils.auth import PostgresDB


def get_bpolys_from_database(table: str, feature_id: int) -> FeatureCollection:
    """Get geometry and properties from geo database as a geojson feature collection."""

    db = PostgresDB()

    # TODO: adjust this for other input tables
    query = sql.SQL(
        """
        SET SCHEMA 'benni_test';
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
                        'iso_code', iso_code,
                        'country', country,
                        'region', region
                    )
                )
            )
        )
        FROM {}
        WHERE fid = %(feature_id)s
    """
    ).format(sql.Identifier(table))
    data = {"feature_id": feature_id}
    query_results = db.retr_query(query=query, data=data)
    bpolys = FeatureCollection(query_results[0][0])
    return bpolys
