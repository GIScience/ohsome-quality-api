---- OQAPI Query
WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON (%s), 4326) AS geom
)
SELECT
    SUM(length_osm_buffer_10),
    SUM(length)
FROM
    {table_name},
    bpoly
WHERE
    ST_Intersects ({table_name}.geom, bpoly.geom)
    -- middle point of line within AOI
    AND ST_Within (ST_LineInterpolatePoint ({table_name}.geom, 0.5), bpoly.geom);