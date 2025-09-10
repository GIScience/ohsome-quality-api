WITH bpoly AS (
    SELECT
        ST_SetSRID(ST_GeomFromGeoJSON($$1), 4326) AS geom
)
SELECT
    DATE_TRUNC('month', c.valid_from) AS month,
    $aggregation
FROM
    $contributions_table c,
    bpoly b
WHERE
    ST_Intersects(c.geom, b.geom)
    AND (status_geom_type).status = 'latest'  -- excludes deleted
    AND ($filter)
GROUP BY
    month
ORDER BY
    month;
