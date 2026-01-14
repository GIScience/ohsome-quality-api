WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
        SUM(
            CASE
                WHEN lanes is not NULL AND "FSZ" is not NULL
                     AND (name is not NULL or "ref" is not null) AND "NAM" is not NULL
                     AND oneway is not NULL AND "FAR" is not NULL
                     AND surface is not NULL AND "OFM" is not NULL
                     AND width is not NULL AND "BRF" is not NULL THEN 1
                ELSE 0
            END
        ) AS present_in_both,
        SUM(
        CASE
            WHEN lanes is not NULL AND "FSZ" is NULL
                 AND (name is not NULL or "ref" is not NULL) AND "NAM" is NULL
                 AND oneway is not NULL AND "FAR" is NULL
                 AND surface is not NULL AND "OFM" is NULL
                 AND width is not NULL AND "BRF" is NULL THEN 1
            ELSE 0
        END
    ) AS osm_only,
		SUM(
			CASE
				WHEN lanes IS NULL AND "FSZ" IS NOT NULL
				     AND name is NULL AND "ref" is NULL AND "NAM" is not NULL
                     AND oneway is NULL AND "FAR" is not NULL
                     AND surface is NULL AND "OFM" is not NULL
                     AND width is NULL AND "BRF" is not NULL THEN 1
				ELSE 0
			end
		) AS bkg_only,
        SUM(
        CASE
            WHEN lanes is NULL AND "FSZ" is NULL
                 AND name is NULL AND "ref" is NULL AND "NAM" is NULL
                 AND oneway is NULL AND "FAR" is NULL
                 AND surface is NULL AND "OFM" is NULL
                 AND width is NULL AND "BRF" is NULL THEN 1
            ELSE 0
        END
        ) AS missing_both,
        SUM(
            CASE
                WHEN lanes is not NULL
                     AND "FSZ" is not NULL
                     AND (name is not NULL or "ref" is not null) AND "NAM" is not NULL
                     AND oneway is not NULL AND "FAR" is not NULL
                     AND surface is not NULL AND "OFM" is not NULL
                     AND width is not NULL AND "BRF" is not NULL
                     AND lanes = "FSZ"
		             AND lev_ratio >= 0.8
                     AND oneway = "FAR"
                     AND ((angle_osm > 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm < 0))
                     AND surface = "OFM"
                     AND abs(width - "BRF") > 1
                    THEN 1
                ELSE 0
            END
        ) AS present_in_both_agree,
            SUM(
            CASE
                WHEN lanes is not NULL
                     AND "FSZ" is not NULL
                     AND (name is not NULL or "ref" is not null) AND "NAM" is not NULL
                     AND oneway is not NULL AND "FAR" is not NULL
                     AND surface is not NULL AND "OFM" is not NULL
                     AND width is not NULL AND "BRF" is not NULL
                     AND lanes != "FSZ"
                     AND lev_ratio < 0.8
                     AND (oneway != "FAR"
                     OR ((angle_osm < 0 AND angle_dlm > 0) OR (angle_osm < 0 AND angle_dlm > 0)))
                     AND surface != "OFM"
                     AND abs(width - "BRF") <= 1
                     THEN 1
                ELSE 0
            END
        ) AS present_in_both_not_agree
FROM oqapi_road_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
