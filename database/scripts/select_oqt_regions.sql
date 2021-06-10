/* Select custom OQT regions from NUTS and GADM datasets */
/* European regiongs (NUTS) */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    'Southern Athens' AS name,
    'Greece' AS country,
    ST_Multi (wkb_geometry) AS geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (wkb_geometry) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (wkb_geometry)) AS
	degree_of_urbanisation_name
FROM
    nuts_rg_01m_2021
WHERE
    nuts_id = 'EL304';

INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    'London Westminster' AS name,
    'United Kingdom' AS country,
    ST_Multi (wkb_geometry) AS geom,
    'good' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (wkb_geometry) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (wkb_geometry)) AS
	degree_of_urbanisation_name
FROM
    nuts_rg_01m_2021
WHERE
    nuts_id = 'UKI32';

INSERT INTO regions (
    'Heidelberg' AS name,
    'Germany' AS country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    nuts_name AS name,
    ST_Multi (wkb_geometry) AS geom,
    'good' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (wkb_geometry) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (wkb_geometry)) AS
	degree_of_urbanisation_name
FROM
    nuts_rg_01m_2021
WHERE
    nuts_id = 'DE125';


/* Countries (GADM) */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_0 AS name,
    name_0 AS country,
    geom,
    '?' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_0
WHERE
    name_0 = 'Haiti';

INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_0 AS name,
    name_0 AS country,
    geom,
    '?' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_0
WHERE
    name_0 = 'Dominican Republic';


/* Misc (GADM) */
/* Philippines Manila */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_3 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_3
WHERE
    gid_3 = 'PHL.5.16.22_1';


/* Mali Raz El Ma */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_4 AS name,
    name_0 AS country,
    geom,
    'bad' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_4
WHERE
    gid_4 = 'MLI.9.2.6.1_1';


/* Morocco Fnidq */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_4 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_4
WHERE
    gid_4 = 'MAR.14.5.2.1_1';


/* Tunisia Tunis */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_1 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_1
WHERE
    gid_1 = 'TUN.23_1';


/* Tunisia Remada */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_2 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_2
WHERE
    gid_2 = 'TUN.21.2_1';


/* Monaco */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_0 AS name,
    name_0 AS country,
    geom,
    'good' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_0
WHERE
    gid_0 = 'MCO';


/* Algeria Touggourt */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_2 AS name,
    name_0 AS country,
    geom,
    'bad' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_2
WHERE
    gid_2 = 'DZA.33.20_1';


/* Algeria Bechar */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_2 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_2
WHERE
    gid_2 = 'DZA.7.2_1';


/* Brazil Rio de Janeiro */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_2 AS name,
    name_0 AS country,
    geom,
    'bad' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_2
WHERE
    gid_2 = 'BRA.19.67_1';


/* Germany Saterland */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_3 AS name,
    name_0 AS country,
    geom,
    'medium' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_3
WHERE
    gid_3 = 'DEU.9.5.13_1';


/* Turkey Kangal */
INSERT INTO regions (
    name,
    country,
    geom,
    subjective_quality_expectations,
    degree_of_urbanisation_class,
    degree_of_urbanisation_name)
SELECT
    name_2 AS name,
    name_0 AS country,
    geom,
    'bad' AS subjective_quality_expectations,
    ghsl_degree_of_urbanisation (geom) AS degree_of_urbanisation,
    ghsl_l1_class_to_name (ghsl_degree_of_urbanisation (geom)) AS degree_of_urbanisation_name
FROM
    gadm_level_2
WHERE
    gid_2 = 'TUR.72.10_1';
