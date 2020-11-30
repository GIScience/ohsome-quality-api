ALTER TABLE isea3h_world_res_12_hex
    ADD COLUMN IF NOT EXISTS population FLOAT;

WITH hex_pop AS (
    SELECT
        geohash_id,
        (stats).sum AS population
        -- (stats).count AS pixel_count,
        -- (stats).count * 0.25 * 0.25 AS area_sqkm,
        -- (stats).sum / ((stats).count * 0.25 * 0.25) AS pop_per_sqkm
    FROM (
        SELECT
            geohash_id,
            -- it's important do to the union here and group by rid
            -- otherwise we might count some pixel several times
            ST_SummaryStats (ST_Union (ST_Clip (rast, geom4326))) AS stats
    FROM
        ghs_pop_4326,
        isea3h_world_res_12_hex
    WHERE
        ST_Intersects (rast, geom4326)
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
        AND abs(ST_xMin (geom4326) - ST_xMax (geom4326)) <= 180
        AND abs(ST_yMin (geom4326) - ST_yMax (geom4326)) <= 90
    GROUP BY
        geohash_id) AS summary_stats)
UPDATE
    isea3h_world_res_12_hex AS hex
SET
    population = hex_pop.population
FROM
    hex_pop
WHERE
    hex.geohash_id = hex_pop.geohash_id;
