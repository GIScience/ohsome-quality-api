---- OQAPI Query
WITH bpoly AS (
    SELECT
        ST_Setsrid(ST_GeomFromGeoJSON(%s), 4326) AS geom
)
SELECT
    SUM(mrc.covered),
    SUM(mrc.length)
FROM
    bpoly
LEFT JOIN {table_name_features} cr ON ST_Intersects(cr.geom, bpoly.geom) AND ST_Within(ST_LineInterpolatePoint(cr.geom, 0.5), bpoly.geom)
LEFT JOIN {table_name_stats} mrc ON cr.id = mrc.id;