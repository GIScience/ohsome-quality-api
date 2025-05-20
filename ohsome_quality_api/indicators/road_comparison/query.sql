WITH bpoly AS (
    SELECT
        -- split mutlipolygon into list of polygons for more efficient processing
        (ST_DUMP (ST_Setsrid (ST_GeomFromGeoJSON ($1), 4326))).geom AS geom
)
SELECT
    SUM(cr.covered),
    SUM(cr.length)
FROM
    bpoly
    LEFT JOIN {table_name} cr ON ST_Intersects (cr.midpoint, bpoly.geom);
