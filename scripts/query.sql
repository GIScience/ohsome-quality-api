ALTER TABLE isea3h_world_res_12_hex
    ADD COLUMN IF NOT EXISTS ghs_pop INTEGER;

SELECT DISTINCT
    geohash_id AS hex_cell,
    rid AS pop_cell
FROM (
    SELECT
        *
    FROM
        isea3h_world_res_12_hex,
        ghs_pop
    WHERE
        ST_Intersects (rast, ST_Transform (geom, 54009))
        AND geohash_id = 4489394) AS foo;
