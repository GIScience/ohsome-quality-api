SELECT
    ST_AsGeoJSON (ST_Transform ($1, 4326)) as geom
FROM
    building_comparison_metadata
WHERE
    name like $2;


