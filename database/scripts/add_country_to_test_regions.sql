/* Add certain countries to the test regions */
INSERT INTO test_regions (geom, infile)
SELECT
    geom,
    name_0 AS infile
FROM
    gadm_level_0
WHERE
    name_0 = 'Bangladesh'
    OR name_0 = 'Dominican Republic'
    OR name_0 = 'Haiti'
    OR name_0 = 'Myanmar'
    OR name_0 = 'South Sudan';
