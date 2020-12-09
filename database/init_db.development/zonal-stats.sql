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
            public.ST_SummaryStats (public.ST_Union (public.ST_Clip (rast, public.ST_Transform (geom, 954009)))) AS stats
    FROM
        ghs_pop,
        isea3h_world_res_12_hex
    WHERE
        public.ST_Intersects (rast, public.ST_Transform (geom, 954009))
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
        AND abs(public.ST_xMin (public.ST_Transform (geom, 954009)) - public.ST_xMax (public.ST_Transform (geom, 954009))) < 100000
        AND abs(public.ST_yMin (public.ST_Transform (geom, 954009)) - public.ST_yMax (public.ST_Transform (geom, 954009))) < 100000
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


ALTER TABLE isea3h_world_res_6_hex
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
            public.ST_SummaryStats (public.ST_Union (public.ST_Clip (rast, public.ST_Transform (geom, 954009)))) AS stats
    FROM
        ghs_pop,
        isea3h_world_res_6_hex
    WHERE
        public.ST_Intersects (rast, public.ST_Transform (geom, 954009))
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
        AND abs(public.ST_xMin (public.ST_Transform (geom, 954009)) - public.ST_xMax (public.ST_Transform (geom, 954009))) < 100000
        AND abs(public.ST_yMin (public.ST_Transform (geom, 954009)) - public.ST_yMax (public.ST_Transform (geom, 954009))) < 100000
    GROUP BY
        geohash_id) AS summary_stats)
UPDATE
    isea3h_world_res_6_hex AS hex
SET
    population = hex_pop.population
FROM
    hex_pop
WHERE
    hex.geohash_id = hex_pop.geohash_id;


ALTER TABLE isea3h_world_res_6_hex
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
            public.ST_SummaryStats (public.ST_Union (public.ST_Clip (rast, public.ST_Transform (geom, 954009)))) AS stats
    FROM
        ghs_pop,
        isea3h_world_res_6_hex
    WHERE
        public.ST_Intersects (rast, public.ST_Transform (geom, 954009))
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
        AND abs(public.ST_xMin (public.ST_Transform (geom, 954009)) - public.ST_xMax (public.ST_Transform (geom, 954009))) < 100000
        AND abs(public.ST_yMin (public.ST_Transform (geom, 954009)) - public.ST_yMax (public.ST_Transform (geom, 954009))) < 100000
    GROUP BY
        geohash_id) AS summary_stats)
UPDATE
    isea3h_world_res_6_hex AS hex
SET
    population = hex_pop.population
FROM
    hex_pop
WHERE
    hex.geohash_id = hex_pop.geohash_id;


ALTER TABLE nuts_rg_01m_2021
    ADD COLUMN IF NOT EXISTS population FLOAT;

WITH nuts_rg_01m_2021_pop AS (
    SELECT
        id,
        (stats).sum AS population
        -- (stats).count AS pixel_count,
        -- (stats).count * 0.25 * 0.25 AS area_sqkm,
        -- (stats).sum / ((stats).count * 0.25 * 0.25) AS pop_per_sqkm
    FROM (
        SELECT
            id,
            -- it's important do to the union here and group by rid
            -- otherwise we might count some pixel several times
            public.ST_SummaryStats (public.ST_Union (public.ST_Clip (rast, public.ST_Transform (geom, 954009)))) AS stats
    FROM
        ghs_pop,
        nuts_rg_01m_2021
    WHERE
        public.ST_Intersects (rast, public.ST_Transform (geom, 954009))
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
    GROUP BY
        id) AS summary_stats)
UPDATE
    nuts_rg_01m_2021
SET
    population = nuts_rg_01m_2021_pop.population
FROM
    nuts_rg_01m_2021_pop
WHERE
    nuts_rg_01m_2021.id = nuts_rg_01m_2021_pop.id;


ALTER TABLE nuts_rg_60m_2021
    ADD COLUMN IF NOT EXISTS population FLOAT;

WITH nuts_rg_60m_2021_pop AS (
    SELECT
        id,
        (stats).sum AS population
        -- (stats).count AS pixel_count,
        -- (stats).count * 0.25 * 0.25 AS area_sqkm,
        -- (stats).sum / ((stats).count * 0.25 * 0.25) AS pop_per_sqkm
    FROM (
        SELECT
            id,
            -- it's important do to the union here and group by rid
            -- otherwise we might count some pixel several times
            public.ST_SummaryStats (public.ST_Union (public.ST_Clip (rast, public.ST_Transform (geom, 954009)))) AS stats
    FROM
        ghs_pop,
        nuts_rg_60m_2021
    WHERE
        public.ST_Intersects (rast, public.ST_Transform (geom, 954009))
        -- Ignore grid cells at the very edge of the globe to avoid following ERROR:
        -- rt_raster_new: Dimensions requested exceed the maximum permitted for a raster.
    GROUP BY
        id) AS summary_stats)
UPDATE
    nuts_rg_60m_2021
SET
    population = nuts_rg_60m_2021_pop.population
FROM
    nuts_rg_60m_2021_pop
WHERE
    nuts_rg_60m_2021.id = nuts_rg_60m_2021_pop.id;