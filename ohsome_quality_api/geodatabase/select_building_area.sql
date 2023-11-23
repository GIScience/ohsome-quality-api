WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON ($1), 4326) AS geom
)
SELECT
    SUM(eubucco.area) as area
FROM
    eubucco,
    bpoly
WHERE
    ST_Intersects (eubucco.centroid, bpoly.geom);
