WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
        SUM(
            CASE
                WHEN lanes is not NULL AND fsz is not NULL THEN 1
                ELSE 0
            END
        ) AS present_in_both,
        SUM(
        CASE
            WHEN lanes is not NULL AND fsz is NULL THEN 1
            ELSE 0
        END
    ) AS only_osm,
		SUM(
			CASE
				WHEN lanes IS NULL AND fsz IS NOT NULL THEN 1
				ELSE 0
			end
		) AS only_dlm,
        SUM(
        CASE
            WHEN lanes is NULL AND fsz is NULL THEN 1
            ELSE 0
        END
        ) AS missing_both,
        SUM(
            CASE
                WHEN lanes is not NULL
                     AND fsz is not NULL
                     AND lanes = fsz THEN 1
                ELSE 0
            END
        ) AS present_in_both_agree,
            SUM(
            CASE
                WHEN lanes is not NULL
                     AND fsz is not NULL
                     AND lanes != fsz THEN 1
                ELSE 0
            END
        ) AS present_in_both_not_agree
FROM road_thematic_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
