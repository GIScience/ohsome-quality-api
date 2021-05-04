/* */
/* The purpose of this SQL script is to create a schema with datasets for development.*/
/* The schema including its data can be dumped using pg_dump. */
/* This is usefull to setup a local development database. */
/* It is used as basis for the development database inside a Docker container. */
/* */
SET search_path TO public, development;

DROP TABLE IF EXISTS development.regions;

DROP TABLE IF EXISTS development.ghs_pop;

DROP SCHEMA IF EXISTS development;

CREATE SCHEMA IF NOT EXISTS development;

CREATE TABLE development.regions (
    LIKE public.regions INCLUDING INDEXES
);

CREATE TABLE development.ghs_pop (
    LIKE public.ghs_pop INCLUDING INDEXES
);


/* Exclude big regions */
INSERT INTO development.regions
SELECT
    *
FROM
    public.regions;

INSERT INTO development.ghs_pop
SELECT
    rid,
    ST_Clip (rast, ST_Buffer (geom, 0.01), TRUE) AS rast
FROM
    public.ghs_pop,
    development.regions
WHERE
    ST_Intersects (rast, geom)
    AND ST_BandIsNoData (rast) = FALSE;

SELECT
    AddRasterConstraints ('development'::name, 'ghs_pop'::name, 'rast'::name);
