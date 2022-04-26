-- Export OQT regions from database as GeoJSON FeatureCollection.
-- In production the OQT website uses a GeoJSON FeatureCollection with the QOT regions
-- to avoid making a request to the OQT API in order to fetch those regions.
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type',       'Feature',
            'id',         ogc_fid,
            'geometry',   ST_AsGeoJSON(geom)::json,
            'properties', json_build_object(
                -- list of fields
                'name', name
            )
        )
    )
)
FROM regions;
