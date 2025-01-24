WITH bpoly AS (
    SELECT
        to_geometry (from_geojson_geometry ('{geometry}')) AS geometry
)
SELECT
    Sum(
        CASE WHEN ST_Within (ST_GeometryFromText (contributions.geometry), bpoly.geometry) THEN
            length
        ELSE
            Cast(ST_Length (ST_Intersection (ST_GeometryFromText (contributions.geometry), bpoly.geometry)) AS integer)
        END) AS length
FROM
    bpoly,
    sotm2024_iceberg.geo_sort.contributions AS contributions
WHERE
    status = 'latest'
    AND ST_Intersects (bpoly.geometry, ST_GeometryFromText (contributions.geometry))
    AND {filter}
    AND (bbox.xmax <= {bounding_box.lon_max} AND bbox.xmin >= {bounding_box.lon_min})
    AND (bbox.ymax <= {bounding_box.lat_max} AND bbox.ymin >= {bounding_box.lat_min})
