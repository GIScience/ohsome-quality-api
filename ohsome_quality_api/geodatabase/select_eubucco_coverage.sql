SELECT
    ST_AsGeoJSON (ST_Transform (geom, 4326)) as geom
FROM
    eubucco_v0_1_coverage_simple;
