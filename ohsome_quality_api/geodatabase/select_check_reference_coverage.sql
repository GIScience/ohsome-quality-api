WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON ($1), 4326) AS geom
)
SELECT
    -- ratio of area within coverage (empty if outside, between 0-1 if intersection)
    ST_Area (ST_Intersection (bpoly.geom, coverage.geom)) / ST_Area (bpoly.geom) as area_ratio
FROM
    bpoly,
    {coverage_name} coverage
WHERE
    ST_Intersects (bpoly.geom, coverage.geom)
