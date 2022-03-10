/* */
/* The purpose of this SQL script is to create a schema with datasets for development.*/
/* The schema including its data can be dumped using pg_dump. */
/* This is useful to setup a local development database. */
/* It is used as basis for the development database inside a Docker container. */
/* */
SET search_path TO public, development, test;

DROP TABLE IF EXISTS development.regions;

DROP TABLE IF EXISTS test.regions;

DROP TABLE IF EXISTS development.ghs_pop;

DROP TABLE IF EXISTS test.ghs_pop;

DROP TABLE IF EXISTS development.shdi;

DROP TABLE IF EXISTS test.shdi;

DROP SCHEMA IF EXISTS development;

DROP SCHEMA IF EXISTS test;
