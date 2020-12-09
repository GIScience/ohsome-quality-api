ALTER TABLE isea3h_world_res_6_hex
    ADD COLUMN IF NOT EXISTS area FLOAT;

ALTER TABLE isea3h_world_res_12_hex
    ADD COLUMN IF NOT EXISTS area FLOAT;

WITH hex_area AS (
    SELECT
        geohash_id,
        ST_Area (geom4326::geography) AS area
    FROM
        isea3h_world_res_6_hex)
UPDATE
    isea3h_world_res_6_hex AS hex
SET
    area = hex_area.area
FROM
    hex_area
WHERE
    hex.geohash_id = hex_area.geohash_id;

WITH hex_area AS (
    SELECT
        geohash_id,
        ST_Area (geom4326::geography) AS area
    FROM
        isea3h_world_res_12_hex)
UPDATE
    isea3h_world_res_12_hex AS hex
SET
    area = hex_area.area
FROM
    hex_area
WHERE
    hex.geohash_id = hex_area.geohash_id;
