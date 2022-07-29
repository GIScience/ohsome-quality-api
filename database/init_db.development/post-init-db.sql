/* Minimal database setup for testing purposes. */
/* If data for development exists give it precedence over test setup. */
/* This includes also data needed for testing. */
DO $$
BEGIN
    IF (
        SELECT
            EXISTS (
            SELECT
                *
            FROM
                INFORMATION_SCHEMA.TABLES
            WHERE
                TABLE_SCHEMA = 'development' AND TABLE_NAME = 'regions')) THEN
        ALTER TABLE development.regions SET SCHEMA public;
        ALTER TABLE development.shdi SET SCHEMA public;
        ALTER TABLE development.hexcells SET SCHEMA public;
        ALTER TABLE development.admin_world_water SET SCHEMA public;
    ELSE
        ALTER TABLE test.regions SET SCHEMA public;
        ALTER TABLE test.shdi SET SCHEMA public;
        ALTER TABLE test.hexcells SET SCHEMA public;
    END IF;
END;
$$
LANGUAGE plpgsql;

DROP TABLE IF EXISTS development.regions;

DROP TABLE IF EXISTS development.shdi;

DROP TABLE IF EXISTS development.hexcells;

DROP TABLE IF EXISTS development.admin_world_water;

DROP TABLE IF EXISTS test.regions;

DROP TABLE IF EXISTS test.shdi;

DROP TABLE IF EXISTS test.hexcells;

DROP SCHEMA IF EXISTS test CASCADE;

DROP SCHEMA IF EXISTS development CASCADE;
