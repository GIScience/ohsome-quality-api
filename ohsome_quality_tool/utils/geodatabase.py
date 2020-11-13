from geojson import FeatureCollection
from psycopg2 import sql

from ohsome_quality_tool.utils.auth import PostgresDB


def get_bpolys_from_database(table: str, feature_id: int) -> FeatureCollection:
    """Get geometries from geo database as a geojson feature collection."""

    db = PostgresDB()

    query = f"""
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
                    'geometry',   ST_AsGeoJSON(geom)::json,
                    'properties', json_build_object(
                        -- list of fields
                        'iso_code', iso_code,
                        'country', country,
                        'region', region
                    )
                )
            )
        )
        FROM benni_test.{sql.Identifier(table)}
        WHERE fid = %(feature_id)s
    """

    data = {"feature_id": feature_id}
    query_results = db.retr_query(query, data)
    print(query_results)
    bpolys = ""
    return bpolys
