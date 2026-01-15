WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    SUM(dlm_length) as total_dlm,
        SUM(
            CASE
                WHEN oneway is not NULL AND far is not NULL THEN dlm_length
                ELSE 0
            END
        ) AS present_in_both,
        SUM(
        CASE
            WHEN oneway is not NULL AND far is NULL THEN dlm_length
            ELSE 0
        END
    ) AS only_osm,
		SUM(
			CASE
				WHEN oneway IS NULL AND far IS NOT NULL THEN dlm_length
				ELSE 0
			end
		) AS only_dlm,
        SUM(
        CASE
            WHEN oneway is NULL AND far is NULL THEN dlm_length
            ELSE 0
        END
        ) AS missing_both,
        SUM(
            CASE
                WHEN oneway is not NULL
                     AND far is not NULL
                     AND oneway = far
                     AND ((angle_osm > 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm < 0)) THEN dlm_length
                ELSE 0
            END
        ) AS present_in_both_agree,
            SUM(
            CASE
                WHEN oneway is not NULL
                     AND far is not NULL
                     AND (oneway != far
                     OR ((angle_osm < 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm > 0))
                     ) THEN dlm_length
                ELSE 0
            END
        ) AS present_in_both_not_agree,
        SUM(
            CASE
                WHEN osm_id IS NULL THEN dlm_length
                ELSE 0
            END
        ) AS not_matched
FROM road_thematic_accuracy rta, bpoly b
WHERE
    ST_Intersects(rta.geom, b.geometry);
