WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    SUM(dlm_length) as total_dlm,
        SUM(
                CASE
                    WHEN surface is not NULL AND ofm is not NULL THEN dlm_length
                    ELSE 0
                END
            ) AS present_in_both,
        SUM(
            CASE
                WHEN surface is not NULL AND ofm is NULL THEN dlm_length
                ELSE 0
            END
        ) AS only_osm,
        SUM(
                CASE
                    WHEN surface IS NULL AND ofm IS NOT NULL THEN dlm_length
                    ELSE 0
                end
            ) AS only_dlm,
        SUM(
            CASE
                WHEN surface is NULL AND ofm is NULL THEN dlm_length
                ELSE 0
            END
        ) AS missing_both,
        SUM(
            CASE
                WHEN surface is not NULL
                     AND ofm is not NULL
                     AND surface = ofm THEN dlm_length
                ELSE 0
            END
        ) AS present_in_both_agree,
        SUM(
            CASE
                WHEN surface is not NULL
                     AND ofm is not NULL
                     AND surface != ofm THEN dlm_length
                ELSE 0
            END
        ) AS present_in_both_not_agree,
        SUM(
            CASE
                WHEN osm_id IS NULL THEN dlm_length
                ELSE 0
            END
        ) AS not_matched
FROM road_thematic_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
