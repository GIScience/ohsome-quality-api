WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
        SUM(
                CASE
                    WHEN width is not NULL AND "BRF" is not NULL THEN 1
                    ELSE 0
                END
            ) AS present_in_both,
        SUM(
            CASE
                WHEN width is not NULL AND "BRF" is NULL THEN 1
                ELSE 0
            END
        ) AS osm_only,
        SUM(
                CASE
                    WHEN width IS NULL AND "BRF" IS NOT NULL THEN 1
                    ELSE 0
                end
            ) AS bkg_only,
        SUM(
            CASE
                WHEN width is NULL AND "BRF" is NULL THEN 1
                ELSE 0
            END
        ) AS missing_both,
        SUM(
            CASE
                WHEN width is not NULL
                     AND "BRF" is not NULL
                     AND abs(width - "BRF") > 1 THEN 1
                ELSE 0
            END
        ) AS present_in_both_agree,
        SUM(
            CASE
                WHEN width is not NULL
                     AND "BRF" is not NULL
                     AND abs(width - "BRF") <= 1 THEN 1
                ELSE 0
            END
        ) AS present_in_both_not_agree
FROM oqapi_road_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
