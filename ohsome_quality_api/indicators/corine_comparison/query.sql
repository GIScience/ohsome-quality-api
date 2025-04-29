-- (8.5, 49.5, 9.0, 50.0)
WITH bpoly AS (
    SELECT
        -- split mutlipolygon into list of polygons for more efficient processing
        (ST_Dump (ST_SetSRID (ST_GeomFromGeoJSON (%s), 4326))).geom AS geom
)
SELECT
    CASE WHEN ST_Within (geometry, bpoly) THEN
        area
    ELSE
        ST_Area (ST_Intersection (geometry, bpoly))::geography)
    END AS area
FROM
    osm_corine_intersection
WHERE
    ST_Intersects (geometry, bpoly);
