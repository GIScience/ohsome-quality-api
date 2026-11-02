WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

SELECT
    SUM(length) AS total_dlm,
    SUM(
        CASE
            WHEN dhu IS NOT NULL AND dhu_osm IS NOT NULL THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS present_in_both,
    SUM(
        CASE
            WHEN dhu IS NULL AND dhu_osm IS NOT NULL THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS only_osm,
    SUM(
        CASE
            WHEN dhu IS NOT NULL AND dhu_osm IS NULL THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS only_dlm,
    SUM(
        CASE
            WHEN dhu IS NULL AND dhu_osm IS NULL THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS missing_both,
    SUM(
        CASE
            WHEN dhu IS NOT NULL
                 AND dhu_osm IS NOT NULL
                 AND abs(dhu - dhu_osm) <= 0.5 THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS present_in_both_agree,
    SUM(
        CASE
            WHEN dhu IS NOT NULL
                 AND dhu_osm IS NOT NULL
                 AND abs(dhu - dhu_osm) > 0.5 THEN length_in_osmbuffer
            ELSE 0
        END
    ) AS present_in_both_not_agree,
    SUM(length - length_in_osmbuffer) AS not_matched
FROM bridge_thematic_accuracy bta, bpoly b
WHERE
    ST_Intersects(bta.geom, b.geometry);
