SELECT
    ST_AsGeoJSON (ST_Transform (geom, 4326)) as geom
FROM
    {table_name};
