---- OQAPI Query
WITH bpoly AS (
    SELECT
        ST_Setsrid (ST_GeomFromGeoJSON ('{
        "coordinates": [
          [
            [
              14.401600308089286,
              35.98854348048188
            ],
            [
              14.401600308089286,
              35.9033309465853
            ],
            [
              14.495720596358126,
              35.9033309465853
            ],
            [
              14.495720596358126,
              35.98854348048188
            ],
            [
              14.401600308089286,
              35.98854348048188
            ]
          ]
        ],
        "type": "Polygon"
      }'), 4326) AS geom
)
SELECT
    SUM(length_osm_buffer_10) / SUM(length)::float8 AS ratio
FROM
    oqapi.microsoft_roads_europe_2022_06_08 ms,
    bpoly
WHERE
    ST_Intersects (ms.geom, bpoly.geom)
    -- middle point of line within AOI
    AND ST_Within (ST_LineInterpolatePoint (ms.geom, 0.5), bpoly.geom);