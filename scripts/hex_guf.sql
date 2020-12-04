SELECT
    geohash_id,
    SUM(ST_Area ((pixel_as_polygon).geom::geography))
FROM (
    SELECT
        geohash_id,
        -- ST_PixelAsPolygons will exclude pixel with nodata values
        ST_PixelAsPolygons (ST_Clip (rast, geom4326)) AS pixel_as_polygon
    FROM
        guf04_daressalaam,
        isea3h_world_res_12_hex
    WHERE
        ST_Intersects (rast, geom4326)
        -- Avoid following ERROR of rt_raster_from_two_rasters during ST_Clip:
        -- The two rasters provided do not have the same alignment
        AND ST_BandIsNoData (rast) = FALSE
    GROUP BY
        geohash_id,
        pixel_as_polygon
    LIMIT 1) AS foo
GROUP BY
    geohash_id;

