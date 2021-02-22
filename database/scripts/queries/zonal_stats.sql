SET SCHEMA 'development';
-- get the raster pixel for the hexgrids with osm contributions
DROP TABLE IF EXISTS nuts_rg_01m_2021_pop;
CREATE TABLE nuts_rg_01m_2021_pop AS
SELECT
  id
  ,geom
  ,(stats).sum as population
  ,(stats).count as pixel_count
  ,(stats).count * 0.25 * 0.25 as area_sqkm
  ,(stats).sum / ((stats).count * 0.25 * 0.25) as pop_per_sqkm
FROM
(
SELECT
  a.id
  ,a.geom
  -- it's important do to the union here and group by rid
  -- otherwise we might count some pixel several times
  ,public.ST_SummaryStats(public.ST_Union(public.ST_Clip(rast, public.ST_Transform(geom, 954009)))) stats
FROM ghs_pop as pop, nuts_rg_01m_2021 as a
WHERE public.ST_Intersects(pop.rast, public.ST_Transform(a.geom, 954009))
GROUP BY
  a.id
  ,a.geom
) as foo;