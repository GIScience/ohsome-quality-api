/* */
/* The purpose of this SQL script is to create a schema with datasets for development.*/
/* The schema including its data can be dumped using pg_dump. */
/* This is usefull to setup a local development database. */
/* It is used as basis for the development database inside a Docker container */
/* */
SET search_path TO public, development;

CREATE SCHEMA IF NOT EXISTS development;

DROP TABLE IF EXISTS development.ghs_pop;

/* */
/* TODO: Does not work with pg_restore due to column defaults pointing to public table. */
/* DROP TABLE IF EXISTS development.oqt_regions; */
/* CREATE TABLE development.oqt_regions ( */
/*     /1* LIKE public.oqt_regions INCLUDING ALL *1/ */
/*     LIKE public.oqt_regions */
/* ); */
/* INSERT INTO development.oqt_regions */
/* SELECT */
/*     * */
/* FROM */
/*     public.oqt_regions; */
/* */
CREATE TABLE development.ghs_pop AS
SELECT
    rid,
    ST_Clip (rast, ST_Buffer (geom, 0.01), TRUE) AS rast
FROM
    public.ghs_pop,
    public.oqt_regions
WHERE
    ST_Intersects (rast, geom)
    AND ST_BandIsNoData (rast) = FALSE;

CREATE INDEX dev_ghs_pop_st_convexhull_idx ON development.ghs_pop USING gist
    (ST_ConvexHull (rast));

SELECT
    AddRasterConstraints ('development'::name, 'ghs_pop'::name, 'rast'::name);
