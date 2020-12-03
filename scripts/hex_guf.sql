SELECT
    geohash_id,
    SUM(ST_Area ((pixel_as_polygon).geom::geography))
FROM (
    SELECT
        geohash_id,
        -- ST_PixelAsPolygons will exclude pixel with nodata values
        ST_PixelAsPolygons (ST_Clip (rast, geom4326)) AS pixel_as_polygon
    FROM
        guf04,
        isea3h_world_res_12_hex
    WHERE
        ST_Intersects (rast, geom4326)
    GROUP BY
        geohash_id,
        pixel_as_polygon
    LIMIT 1) AS foo
GROUP BY
    geohash_id;
