/* */
/* The purpose of this SQL script is to create a schema with datasets for development.*/
/* The schema including its data can be dumped using pg_dump. */
/* This is usefull to setup a local development database. */
/* It is used as basis for the development database inside a Docker container. */
/* */
SET search_path TO public, development;

CREATE SCHEMA IF NOT EXISTS development;

DROP TABLE IF EXISTS development.ghs_pop;

DROP TABLE IF EXISTS development.regions;

CREATE TABLE development.regions (
    LIKE public.regions INCLUDING INDEXES
);


/* Exclude big regions */
INSERT INTO development.regions
SELECT
    *
FROM
    public.regions
WHERE
    name != 'Bangladesh'
    OR name != 'Dominican Republic'
    OR name != 'Haiti'
    OR name != 'Myanmar'
    OR name != 'South Sudan';

CREATE TABLE development.ghs_pop AS
SELECT
    rid,
    ST_Clip (rast, ST_Buffer (geom, 0.01), TRUE) AS rast
FROM
    public.ghs_pop,
    development.regions
WHERE
    ST_Intersects (rast, geom)
    AND ST_BandIsNoData (rast) = FALSE;

CREATE INDEX dev_ghs_pop_st_convexhull_idx ON development.ghs_pop USING gist
    (ST_ConvexHull (rast));

SELECT
    AddRasterConstraints ('development'::name, 'ghs_pop'::name, 'rast'::name);
