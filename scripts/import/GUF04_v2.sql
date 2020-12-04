CREATE INDEX guf04_st_convexhull_idx ON guf04 USING gist (ST_ConvexHull (rast)
SELECT
    AddRasterConstraints ('guf04'::name, 'rast'::name);

VACUUM (ANALYZE) guf04;

DELETE FROM guf04
WHERE NOT rid IN (
        SELECT
            rid
        FROM
            guf04
        GROUP BY
            rid
        HAVING
            ST_ValueCount (rast, 1, TRUE, 255) > 0);
