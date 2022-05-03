/* */
/* The purpose of this SQL script is to create schemas with data for development and testing. */
/* Data for testing is smaller. */
/* The schema including its data can be dumped using pg_dump. */
/* This is useful to setup a local development or testing database. */
/* It is used as basis for the development database inside a Docker container. */
/* */
SET search_path TO public, development, test;


/* Development */
CREATE SCHEMA IF NOT EXISTS development;

CREATE TABLE development.regions (
    LIKE public.regions INCLUDING INDEXES
);

CREATE TABLE development.shdi (
    LIKE public.shdi INCLUDING INDEXES
);

CREATE TABLE development.hexcells (
    LIKE public.hexcells INCLUDING INDEXES
);

INSERT INTO development.regions
SELECT
    *
FROM
    public.regions;

INSERT INTO development.shdi SELECT DISTINCT ON (gid)
    public.shdi.*
FROM
    public.shdi,
    development.regions
WHERE
    ST_Intersects (public.shdi.geom, development.regions.geom);

INSERT INTO development.hexcells SELECT DISTINCT ON (gid)
    public.hexcells.*
FROM
    public.hexcells,
    development.regions
WHERE
    ST_Intersects (public.hexcells.geom, development.regions.geom);


/* Testing */
/* Currently two regions are used for testing: */
/* Heidelberg: 3*/
/* Algeria Touggourt: 11*/
CREATE SCHEMA IF NOT EXISTS test;

CREATE TABLE test.regions (
    LIKE public.regions INCLUDING INDEXES
);

CREATE TABLE test.shdi (
    LIKE public.shdi INCLUDING INDEXES
);

CREATE TABLE test.hexcells (
    LIKE public.hexcells INCLUDING INDEXES
);

INSERT INTO test.regions
SELECT
    *
FROM
    public.regions
WHERE
    ogc_fid IN (3, 11);

INSERT INTO test.shdi SELECT DISTINCT ON (gid)
    public.shdi.*
FROM
    public.shdi,
    test.regions
WHERE
    ST_Intersects (public.shdi.geom, test.regions.geom);

INSERT INTO test.hexcells SELECT DISTINCT ON (gid)
    public.hexcells.*
FROM
    public.hexcells,
    test.regions
WHERE
    ST_Intersects (public.hexcells.geom, test.regions.geom);
