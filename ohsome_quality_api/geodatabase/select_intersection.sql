WITH bpoly AS (
    SELECT
        ST_SetSRID(ST_GeomFromGeoJSON($1), 4326) AS geom
),
selected_coverage AS (
    SELECT coverage_simple AS coverage
    FROM building_comparison_metadata bcm
    WHERE name LIKE $2
)
SELECT
    -- ratio of area within coverage (empty if outside, between 0-1 if intersection)
    ST_Area(ST_Intersection(bpoly.geom, selected_coverage.coverage)) / ST_Area(bpoly.geom) AS area_ratio,
    ST_AsGeoJSON(ST_Intersection(bpoly.geom, selected_coverage.coverage)) AS geom
FROM
    bpoly,
    selected_coverage
WHERE
    ST_Intersects(bpoly.geom, selected_coverage.coverage);

