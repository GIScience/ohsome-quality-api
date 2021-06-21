/* Subnational HDI for regions within a country */
WITH regions_shdi AS (
    SELECT DISTINCT ON (ogc_fid)
        shdi.shdi,
        regions.ogc_fid AS ogc_fid
    FROM
        shdi,
        regions
    WHERE
        st_intersects (shdi.wkb_geometry, regions.geom)
        AND regions.name != regions.country -- region is not a country
    ORDER BY
        ogc_fid,
        ST_Area (ST_Intersection (shdi.wkb_geometry, regions.geom)) DESC)
UPDATE
    regions
SET
    shdi = regions_shdi.shdi
FROM
    regions_shdi
WHERE
    regions.ogc_fid = regions_shdi.ogc_fid;


/* HDI for countries*/
WITH regions_shdi AS (
    SELECT
        AVG(shdi.shdi) as shdi_avg,
        regions.ogc_fid AS ogc_fid
    FROM
        regions,
        shdi
    WHERE
        shdi.country = regions.country
        AND regions.name = regions.country -- region is a country
    GROUP BY
        regions.ogc_fid
)
UPDATE
    regions
SET
    shdi = regions_shdi.shdi_avg
FROM
    regions_shdi
WHERE
    regions.ogc_fid = regions_shdi.ogc_fid;
