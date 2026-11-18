WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
),
bridges AS (
    SELECT
        -- a DLM bridge counts as matched if at least half of it lies in the OSM buffer
        COALESCE(bta.coverage, 0) >= 0.5 AS matched,
        bta.nam,
        bta.nam_osm,
        bta.lev_ratio
    FROM bridge_thematic_accuracy bta, bpoly b
    WHERE
        ST_Intersects(bta.geom, b.geometry)
)

SELECT
    COUNT(*) AS total_dlm,
    COUNT(*) FILTER (
        WHERE matched AND nam IS NOT NULL AND nam_osm IS NOT NULL
    ) AS present_in_both,
    COUNT(*) FILTER (
        WHERE matched AND nam IS NULL AND nam_osm IS NOT NULL
    ) AS only_osm,
    COUNT(*) FILTER (
        WHERE matched AND nam IS NOT NULL AND nam_osm IS NULL
    ) AS only_dlm,
    COUNT(*) FILTER (
        WHERE matched AND nam IS NULL AND nam_osm IS NULL
    ) AS missing_both,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL
              AND nam_osm IS NOT NULL
              AND lev_ratio >= 0.8
    ) AS present_in_both_agree,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL
              AND nam_osm IS NOT NULL
              AND lev_ratio < 0.8
    ) AS present_in_both_not_agree,
    COUNT(*) FILTER (WHERE NOT matched) AS not_matched
FROM bridges;
