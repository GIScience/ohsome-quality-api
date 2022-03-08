WITH bpoly AS (
    SELECT
        ST_Setsrid (public.ST_GeomFromGeoJSON ($1), 4326) AS geom
)
SELECT
    SUM(ST_Area (ST_Intersection (shdi.geom, bpoly.geom)::geography) / ST_Area
	(bpoly.geom::geography) * shdi.shdi) AS shdi
FROM
    shdi,
    bpoly
WHERE
    ST_Intersects (shdi.geom, bpoly.geom);
