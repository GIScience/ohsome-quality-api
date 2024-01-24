WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON ($1), 4326) AS geom
)
SELECT
    ST_AsGeoJSON (ST_Intersection (bpoly.geom, coverage.geom)) AS geom
FROM
    bpoly,
    {table_name} coverage
WHERE
    ST_Intersects (bpoly.geom, coverage.geom)
