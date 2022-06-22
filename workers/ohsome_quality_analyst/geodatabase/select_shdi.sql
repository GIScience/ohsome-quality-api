WITH bpoly AS (
    SELECT
        ST_Setsrid (public.ST_GeomFromGeoJSON (geojson), 4326) AS geom,
        -- Row number is used to make sure order of result is the same as order of input
        -- (Probably unnecessary)
        row_number() OVER () AS rownumber
    FROM
        unnest(cast($1 AS text[])) AS geojson
)
SELECT
    SUM(ST_Area (ST_Intersection (shdi.geom, bpoly.geom)::geography) / ST_Area
	(bpoly.geom::geography) * shdi.shdi) AS shdi,
    rownumber as rownumber
FROM
    shdi,
    bpoly
WHERE
    ST_Intersects (shdi.geom, bpoly.geom)
GROUP BY
    bpoly.geom,
    bpoly.rownumber
ORDER BY
    bpoly.rownumber;
