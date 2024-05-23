SELECT
    ST_AsGeoJSON (ST_Transform ({coverage_type}, 4326)) as geom
FROM
    comparison_indicators_metadata
WHERE
    dataset_name_snake_case like $1;


