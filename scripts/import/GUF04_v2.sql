CREATE INDEX guf04_st_convexhull_idx ON guf04 USING gist (ST_ConvexHull (rast)
SELECT
    AddRasterConstraints ('guf04'::name, 'rast'::name);

VACUUM (ANALYZE) guf04;

