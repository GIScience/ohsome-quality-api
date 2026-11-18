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
        bta.lev_ratio,
        bta.bro,
        bta.bro_osm,
        -- height is only compared for bridges carrying a road. For all other
        -- bridges height counts as neither present nor missing.
        bta.highway_bridge IS NOT TRUE AS height_not_applicable,
        bta.dhu,
        bta.maxheight
    FROM bridge_thematic_accuracy bta, bpoly b
    WHERE
        ST_Intersects(bta.geom, b.geometry)
)

SELECT
    COUNT(*) AS total_dlm,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL AND nam_osm IS NOT NULL
              AND bro IS NOT NULL AND bro_osm IS NOT NULL
              AND (height_not_applicable OR (dhu IS NOT NULL AND maxheight IS NOT NULL))
    ) AS present_in_both,
    COUNT(*) FILTER (
        WHERE matched
              AND nam_osm IS NOT NULL AND bro_osm IS NOT NULL
              AND (height_not_applicable OR maxheight IS NOT NULL)
              AND (nam IS NULL OR bro IS NULL OR (NOT height_not_applicable AND dhu IS NULL))
    ) AS only_osm,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL AND bro IS NOT NULL
              AND (height_not_applicable OR dhu IS NOT NULL)
              AND (nam_osm IS NULL OR bro_osm IS NULL OR (NOT height_not_applicable AND maxheight IS NULL))
    ) AS only_dlm,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NULL AND nam_osm IS NULL
              AND bro IS NULL AND bro_osm IS NULL
              AND (height_not_applicable OR (dhu IS NULL AND maxheight IS NULL))
    ) AS missing_both,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL AND nam_osm IS NOT NULL
              AND bro IS NOT NULL AND bro_osm IS NOT NULL
              AND (height_not_applicable OR (dhu IS NOT NULL AND maxheight IS NOT NULL))
              AND lev_ratio >= 0.8
              AND abs(bro - bro_osm) <= 0.5
              AND (height_not_applicable OR abs(dhu - maxheight) <= 0.5)
    ) AS present_in_both_agree,
    COUNT(*) FILTER (
        WHERE matched
              AND nam IS NOT NULL AND nam_osm IS NOT NULL
              AND bro IS NOT NULL AND bro_osm IS NOT NULL
              AND (height_not_applicable OR (dhu IS NOT NULL AND maxheight IS NOT NULL))
              AND NOT (
                  lev_ratio >= 0.8
                  AND abs(bro - bro_osm) <= 0.5
                  AND (height_not_applicable OR abs(dhu - maxheight) <= 0.5)
              )
    ) AS present_in_both_not_agree,
    COUNT(*) FILTER (WHERE NOT matched) AS not_matched
FROM bridges;
