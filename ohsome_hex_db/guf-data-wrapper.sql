-- Create foreign data wrapper to access guf04 from settlement infrastructure database:
-- https://gitlab.gistools.geog.uni-heidelberg.de/giscience/disaster-tools/settlement-infrastructure
CREATE EXTENSION postgres_fdw;

CREATE SERVER settlement_infrastructure FOREIGN DATA WRAPPER postgres_fdw OPTIONS (
    host 'localhost',
    port '5432',
    dbname 'pop'
);

CREATE USER MAPPING FOR hexadmin SERVER settlement_infrastructure OPTIONS (
    USER 'read_only_user',
    PASSWORD '6uPBpYXxpNTznB90FMrd7TiWM'
);

CREATE FOREIGN TABLE guf04 (
    rid integer NOT NULL,
    rast raster)
SERVER settlement_infrastructure OPTIONS (
    schema_name 'public',
    table_name 'guf04'
);

