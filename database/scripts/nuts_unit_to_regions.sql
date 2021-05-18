/* Add regions from NUTs to OQT Regions */
/* TODO: Change nuts_id to desired value and maybe also set custom name */
INSERT INTO regions (
    name,
    geom)
SELECT
    name_latin AS name,
    ST_Multi (wkb_geometry) AS geom
FROM
    nuts_rg_60m_2021
WHERE
    nuts_id = 'DE125';
