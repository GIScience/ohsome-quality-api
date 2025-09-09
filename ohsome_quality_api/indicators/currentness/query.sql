WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON ('$aoi'), 4326) AS geom
)
SELECT
    Date_trunc('month', valid_from) AS month,
    Count(*)
FROM
    $contributions_table c,
    bpoly b
WHERE
    ST_Intersects (c.geom, b.geom)
    AND (status_geom_type).status = 'latest'  -- excludes deleted
    AND ($filter)
GROUP BY
    month
ORDER BY
    month;
