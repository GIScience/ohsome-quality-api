SELECT
    ST_Area (
		ST_GeomFromGeoJSON (
			$1
		)::geography
	) AS area;
