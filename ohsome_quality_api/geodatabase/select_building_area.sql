WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON (%s), 4326) AS geom
)
SELECT
    SUM({table_name}.area) as area
FROM {table_name},
    bpoly
WHERE
    ST_Intersects ({table_name}.centroid, bpoly.geom);
