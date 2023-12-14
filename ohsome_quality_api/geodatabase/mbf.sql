WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON (%s), 4326) AS geom
)
SELECT
    SUM(mbf_france.area) as area
FROM
    mbf_france,
    bpoly
WHERE
    ST_Intersects (mbf_france.centroid, bpoly.geom);
