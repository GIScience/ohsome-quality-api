-- TODO: will index on classes make this query faster?
WITH bpoly AS (
    SELECT
        -- split mutlipolygon into list of polygons for more efficient processing
        (ST_Dump(ST_SetSRID(ST_GeomFromGeoJSON($1), 4326))).geom AS geometry
)
SELECT
    CLC_class as clc_class_corine,
    osm_CLC_class as clc_class_osm,
    CASE
        WHEN ST_Within(o.geometry, b.geometry) THEN area
        ELSE ST_Area(ST_Intersection(o.geometry, b.geometry)::geography)
    END AS area
FROM
    osm_corine_intersection o,
    bpoly b
WHERE
    ST_Intersects(o.geometry, b.geometry)
    AND (
        o.CLC_class = $2 OR o.osm_CLC_class = $2
    );
