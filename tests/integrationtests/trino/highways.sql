SELECT
    osm_id
FROM
    sotm2024_iceberg.geo_sort.contributions
WHERE
    status = 'latest'
    AND element_at (tags, 'highway') IS NOT NULL
    AND tags['highway'] IN ('motorway', 'trunk', 'motorway_link',
	'trunk_link', 'primary', 'primary_link', 'secondary',
	'secondary_link', 'tertiary', 'tertiary_link', 'unclassified',
	'residential')
    AND (bbox.xmax >= 8.629761
        AND bbox.xmin <= 8.742371)
    AND (bbox.ymax >= 49.379556
        AND bbox.ymin <= 49.437890)
