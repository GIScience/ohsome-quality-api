WITH bpoly AS (
    SELECT
        -- split mutlipolygon into list of polygons for more efficient processing
        (ST_DUMP (ST_Setsrid (ST_GeomFromGeoJSON ($1), 4326))).geom AS geom
)
SELECT
    SUM({table_name}.area) as area
FROM {table_name},
    bpoly
WHERE
    ST_Intersects ({table_name}.centroid, bpoly.geom);
