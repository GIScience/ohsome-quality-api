WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON (%s), 4326) AS geom
)
SELECT
    SUM(cr.covered),
    SUM(cr.length)
FROM
    bpoly
    LEFT JOIN {table_name} cr ON ST_Intersects (cr.midpoint, bpoly.geom);
