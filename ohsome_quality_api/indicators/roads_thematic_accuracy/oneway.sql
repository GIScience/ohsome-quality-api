WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
        SUM(
            CASE
                WHEN oneway is not NULL AND "FAR" is not NULL THEN 1
                ELSE 0
            END
        ) AS present_in_both,
        SUM(
        CASE
            WHEN oneway is not NULL AND "FAR" is NULL THEN 1
            ELSE 0
        END
    ) AS osm_only,
		SUM(
			CASE
				WHEN oneway IS NULL AND "FAR" IS NOT NULL THEN 1
				ELSE 0
			end
		) AS bkg_only,
        SUM(
        CASE
            WHEN oneway is NULL AND "FAR" is NULL THEN 1
            ELSE 0
        END
        ) AS missing_both,
        SUM(
            CASE
                WHEN oneway is not NULL
                     AND "FAR" is not NULL
                     AND oneway = "FAR"
                     AND ((angle_osm > 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm < 0)) THEN 1
                ELSE 0
            END
        ) AS present_in_both_agree,
            SUM(
            CASE
                WHEN oneway is not NULL
                     AND "FAR" is not NULL
                     AND (oneway != "FAR"
                     OR ((angle_osm < 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm > 0))
                     ) THEN 1
                ELSE 0
            END
        ) AS present_in_both_not_agree
FROM road_accuracy rta, bpoly b
WHERE
    ST_Intersects(rta.geom, b.geometry);
