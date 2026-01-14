WITH bpoly AS (
    SELECT
        -- split multipolygon into individual polygons
    (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON ($1), 4326))).geom AS geometry
)

select
    COUNT(*) as total_dlm,
    SUM(
        CASE
            WHEN (name is not NULL OR "ref" is not NULL) AND "NAM" is not NULL THEN 1
            ELSE 0
        END
    ) AS present_in_both,
        SUM(
        CASE
            WHEN (name is not NULL OR ref is not NULL) AND "NAM" is NULL THEN 1
            ELSE 0
        END
    ) AS osm_only,
		SUM(
			CASE
				WHEN name IS NULL AND ref IS NULL AND "NAM" IS NOT NULL THEN 1
				ELSE 0
			end
		) AS bkg_only,
        SUM(
        CASE
            WHEN name is NULL AND ref is NULL AND "NAM" is NULL THEN 1
            ELSE 0
        END
    ) AS missing_both,
        SUM(
		CASE
		    WHEN (name is not NULL OR "ref" is not NULL)
		         AND "NAM" is not NULL
		         AND lev_ratio >= 0.8 THEN 1
		    ELSE 0
		END
	) AS present_in_both_agree,
	    SUM(
        CASE
            WHEN (name is not NULL OR "ref" is not NULL)
                 AND "NAM" is not NULL
                 AND lev_ratio < 0.8 THEN 1
            ELSE 0
        END
    ) AS present_in_both_not_agree
FROM road_accuracy as ora, bpoly b
WHERE
    ST_Intersects(ora.geom, b.geometry);
