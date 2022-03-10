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
        ALTER TABLE development.ghs_pop SET SCHEMA public;
        ALTER TABLE development.shdi SET SCHEMA public;
    ELSE
        ALTER TABLE test.regions SET SCHEMA public;
        ALTER TABLE test.ghs_pop SET SCHEMA public;
        ALTER TABLE test.shdi SET SCHEMA public;
    END IF;
END;
$$
LANGUAGE plpgsql;

DROP TABLE IF EXISTS development.regions;

DROP TABLE IF EXISTS development.ghs_pop;

DROP TABLE IF EXISTS development.shdi;

DROP TABLE IF EXISTS test.regions;

DROP TABLE IF EXISTS test.ghs_pop;

DROP TABLE IF EXISTS test.shdi;

DROP SCHEMA IF EXISTS test;

DROP SCHEMA IF EXISTS development;
