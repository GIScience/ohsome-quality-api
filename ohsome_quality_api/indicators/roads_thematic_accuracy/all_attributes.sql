WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
        SUM(
            CASE
                WHEN lanes is not NULL AND fsz is not NULL
                     AND (name is not NULL or ref is not null) AND nam is not NULL
                     AND oneway is not NULL AND far is not NULL
                     AND surface is not NULL AND ofm is not NULL
                     AND width is not NULL AND brf is not NULL THEN 1
                ELSE 0
            END
        ) AS present_in_both,
        SUM(
        CASE
            WHEN lanes is not NULL AND fsz is NULL
                 AND (name is not NULL or ref is not NULL) AND nam is NULL
                 AND oneway is not NULL AND far is NULL
                 AND surface is not NULL AND ofm is NULL
                 AND width is not NULL AND brf is NULL THEN 1
            ELSE 0
        END
    ) AS only_osm,
		SUM(
			CASE
				WHEN lanes IS NULL AND fsz IS NOT NULL
				     AND name is NULL AND ref is NULL AND nam is not NULL
                     AND oneway is NULL AND far is not NULL
                     AND surface is NULL AND ofm is not NULL
                     AND width is NULL AND brf is not NULL THEN 1
				ELSE 0
			end
		) AS only_dlm,
        SUM(
        CASE
            WHEN (lanes is NULL AND fsz is NULL)
                 OR (name is NULL AND ref is NULL AND nam is NULL)
                 OR (oneway is NULL AND far is NULL)
                 OR (surface is NULL AND ofm is NULL)
                 OR (width is NULL AND brf is NULL) THEN 1
            ELSE 0
        END
        ) AS missing_both,
        SUM(
            CASE
                WHEN lanes is not NULL
                     AND fsz is not NULL
                     AND (name is not NULL or ref is not null) AND nam is not NULL
                     AND oneway is not NULL AND far is not NULL
                     AND surface is not NULL AND ofm is not NULL
                     AND width is not NULL AND brf is not NULL
                     AND lanes = fsz
		             AND lev_ratio >= 0.8
                     AND oneway = far
                     AND ((angle_osm > 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm < 0))
                     AND surface = ofm
                     AND abs(width - brf) > 1
                    THEN 1
                ELSE 0
            END
        ) AS present_in_both_agree,
            SUM(
            CASE
                WHEN lanes is not NULL
                     AND fsz is not NULL
                     AND (name is not NULL or ref is not null) AND nam is not NULL
                     AND oneway is not NULL AND far is not NULL
                     AND surface is not NULL AND ofm is not NULL
                     AND width is not NULL AND brf is not NULL
                     AND lanes != fsz
                     AND lev_ratio < 0.8
                     AND (oneway != far
                     OR ((angle_osm < 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm > 0)))
                     AND surface != ofm
                     AND abs(width - brf) <= 1
                     THEN 1
                ELSE 0
            END
        ) AS present_in_both_not_agree
FROM road_thematic_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
