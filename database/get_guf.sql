COPY (
    SELECT
        *
    FROM
        public.guf04
    WHERE
        rast && ST_Transform (ST_MakeEnvelope (5.954590, 47.294134, 15.227051, 55.002826, 4326), 954009))
TO 'guf-heidelberg.copy';
