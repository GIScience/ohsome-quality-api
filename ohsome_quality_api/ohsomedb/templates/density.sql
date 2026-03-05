-- WITH poly AS (
--     SELECT ST_GeomFromGeoJSON(${{ geom }}) AS geom
-- ),
-- intersecting AS (
--     SELECT c.geom
--     FROM {{ contributions }} c, poly p
--     WHERE
--         (status_geom_type).status = 'latest'
--         AND valid_to >= NOW()::timestamp
--         AND valid_from < NOW()::timestamp
--         AND ({{ filter }})
--         AND ST_Intersects(c.geom, p.geom)
-- )
-- SELECT
--     NOW()::timestamp AS snapshot_ts,
--     ST_Area(ST_UnaryUnion(ST_Union(i.geom))::geography) AS non_overlapping_geom
-- FROM intersecting i, poly p;

WITH poly AS (
    SELECT ST_GeomFromGeoJSON(${{ geom }}) AS geom
)
SELECT
    NOW()::timestamp AS snapshot_ts,
    ST_Area(ST_UNION(
            ST_Intersection(c.geom, p.geom)
            )::geography) / ST_Area(p.geom::geography) as value
FROM {{ contributions }} c, poly p
WHERE
    (status_geom_type).status = 'latest'
    AND valid_to >= NOW()::timestamp
    AND valid_from < NOW()::timestamp
    AND ({{ filter }})
    AND ST_Intersects(c.geom, p.geom)
GROUP BY p.geom
;

