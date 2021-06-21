/* Utility functions for extracting degree of urbanisation classes of the GHS-SMOD dataset. */
/* */
/* */
/* https://ghsl.jrc.ec.europa.eu/documents/GHSL_Data_Package_2019.pdf */
/* Aggregation of GHS-SMOD L2 class typologies to L1 class typologies */
/* L2: two digit code (30 - 23 - 22 - 21 - 13 - 12 - 11 - 10) */
/* L1: one digit code (3 - 2 - 1) */
/* */
/* L2                 -> L1
/* 30                 -> 3 */
/* 23 - 22 - 21       -> 2 */
/* 13 - 12 - 11 - 10  -> 1 */
CREATE OR REPLACE FUNCTION ghsl_l2_to_l1_class (IN l2_class double precision)
    RETURNS integer
    AS $$
DECLARE
    l1_class integer;
BEGIN
    SELECT
        CAST(LEFT (CAST(l2_class AS text), 1) AS integer) INTO l1_class;
    RETURN l1_class;
END;
$$
LANGUAGE plpgsql;


/* - Class 1: "Rural grid cell", if the cell does not belong to an Urban Cluster */
/* - Class 2: "Urban Cluster grid cell", if the cell belongs to an Urban Cluster and not to an Urban Centre; */
/* - Class 3: "Urban Centre grid cell", if the cell belongs to an Urban Centre; */
/* https://ghsl.jrc.ec.europa.eu/documents/GHSL_Data_Package_2019.pdf */
CREATE OR REPLACE FUNCTION ghsl_l1_class_to_name (IN l1_class integer)
    RETURNS text
    AS $$
DECLARE
    name text;
BEGIN
    SELECT
        CASE l1_class
        WHEN 1 THEN
            'Urban Centre'
        WHEN 2 THEN
            'Urban Cluster'
        WHEN 3 THEN
            'Rural'
        END INTO name;
    RETURN name;
END;
$$
LANGUAGE plpgsql;


/* Returns GHS-SMOD level 1 classification for a vector geometry. */
CREATE OR REPLACE FUNCTION ghsl_degree_of_urbanisation (IN geom geometry)
    RETURNS numeric
    AS $$
DECLARE
    degree_of_urbanisation numeric;
BEGIN
    WITH rast_clip AS (
        SELECT
            ST_Union (ST_Clip (rast, ST_Transform (geom, 54009), 1, TRUE)) AS rast
        FROM
            ghs_smod
        WHERE
            ST_Intersects (rast, ST_Transform (geom, 54009))
    ),
    rast_values AS (
        SELECT
            unnest(ST_DumpValues (rast, 1)) AS value
        FROM
            rast_clip
    )
    SELECT
        round(avg(ghsl_l2_to_l1_class (value))) INTO degree_of_urbanisation
    FROM
        rast_values;
        RETURN degree_of_urbanisation;
END;
$$
LANGUAGE plpgsql;

UPDATE
    regions
SET
    degree_of_urbanisation_class = ghsl_degree_of_urbanisation(geom);

UPDATE
    regions
SET
    degree_of_urbanisation_name= ghsl_l1_class_to_name(degree_of_urbanisation_class);
