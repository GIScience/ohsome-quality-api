-- This SQL Query is meant to be used with psycopg2.
SELECT public.ST_Area (public.ST_GeomFromGeoJSON(%s)::public.geography);
