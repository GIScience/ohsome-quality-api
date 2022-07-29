/* */
/* The purpose of this SQL script is to create a schema with datasets for development.*/
/* The schema including its data can be dumped using pg_dump. */
/* This is useful to setup a local development database. */
/* It is used as basis for the development database inside a Docker container. */
/* */
SET search_path TO public, development, test;

DROP TABLE IF EXISTS development.regions;

DROP TABLE IF EXISTS test.regions;

DROP TABLE IF EXISTS development.shdi;

DROP TABLE IF EXISTS test.shdi;

DROP TABLE IF EXISTS development.hexcells;

DROP TABLE IF EXISTS test.hexcells;

DROP TABLE IF EXISTS development.admin_world_water;

DROP SCHEMA IF EXISTS development;

DROP SCHEMA IF EXISTS test;
