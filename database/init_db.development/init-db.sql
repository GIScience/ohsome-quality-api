CREATE EXTENSION postgis_raster;

-- Add spatial reference system of GHS_POP
INSERT into spatial_ref_sys (srid, auth_name, auth_srid, proj4text, srtext) values ( 954009, 'esri', 54009, '+proj=moll +lon_0=0 +x_0=0 +y_0=0 +ellps=WGS84 +datum=WGS84 +units=m +no_defs ', 'PROJCS["World_Mollweide",GEOGCS["GCS_WGS_1984",DATUM["WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree",0.017453292519943295]],PROJECTION["Mollweide"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["Central_Meridian",0],UNIT["Meter",1],AUTHORITY["EPSG","54009"]]');


CREATE SCHEMA IF NOT EXISTS development;

CREATE TABLE IF NOT EXISTS development.nuts_rg_01m_2021
(
    ogc_fid integer,
    id character varying COLLATE pg_catalog."default",
    coast_type integer,
    mount_type integer,
    name_latn character varying COLLATE pg_catalog."default",
    cntr_code character varying COLLATE pg_catalog."default",
    fid character varying COLLATE pg_catalog."default",
    nuts_id character varying COLLATE pg_catalog."default",
    nuts_name character varying COLLATE pg_catalog."default",
    levl_code integer,
    urbn_type integer,
    geom geometry(Geometry,4326)
);

CREATE TABLE IF NOT EXISTS  development.nuts_rg_60m_2021
(
    ogc_fid integer,
    id character varying COLLATE pg_catalog."default",
    coast_type integer,
    mount_type integer,
    name_latn character varying COLLATE pg_catalog."default",
    cntr_code character varying COLLATE pg_catalog."default",
    fid character varying COLLATE pg_catalog."default",
    nuts_id character varying COLLATE pg_catalog."default",
    nuts_name character varying COLLATE pg_catalog."default",
    levl_code integer,
    urbn_type integer,
    geom geometry(Geometry,4326)
);

CREATE TABLE IF NOT EXISTS  development.isea3h_world_res_6_hex
(
    geohash_id bigint,
    global_id bigint,
    geom4326 geometry(MultiPolygon,4326),
    geom geometry(MultiPolygon,3857),
    pt_geom geometry(Point,3857)
);

CREATE TABLE IF NOT EXISTS  development.isea3h_world_res_12_hex
(
    geohash_id bigint,
    global_id bigint,
    geom4326 geometry(MultiPolygon,4326),
    geom geometry(MultiPolygon,3857),
    pt_geom geometry(Point,3857)
);

CREATE TABLE IF NOT EXISTS  development.guf04
(
    rid integer,
    rast raster
);

