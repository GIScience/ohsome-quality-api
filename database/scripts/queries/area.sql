CREATE FUNCTION calc_area() RETURNS void AS $$
DECLARE
  x int[];
BEGIN
  FOREACH x IN ARRAY $1
  LOOP
    WITH area_table AS (
        SELECT
            id,
            ST_Area (geom4326::geography) AS area
        FROM
            x)
    UPDATE
        x
    SET
        area = area_table.area
    FROM
        area_table
    WHERE
        x.geohash_id = area_table.geohash_id;

  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Execution time: Circa 10 hours
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
