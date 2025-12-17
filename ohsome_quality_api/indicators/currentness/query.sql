-- Parsing the GeoJSON directly in the WHERE clause instead of
-- in a WITH clause makes the query faster
WITH serie AS (
    SELECT
        Generate_series(
            '2007-10-01'::timestamp,
            NOW()::timestamp,
            '1 month'::interval
        )::date AS month
),
contribution AS (
    SELECT
        Date_trunc('month', c.valid_from) AS month,
        $aggregation AS contribution
    FROM
        $contributions_table c
    WHERE 1=1
        -- TODO: this would be more performant but ohsome-filter-to-sql can not generate this
        -- clause because is does not know about "latest"
        -- AND status_geom_type = ANY(ARRAY[('latest', 'Polygon'), ('latest', 'MultiPolygon')]::_status_geom_type_type)
        AND (status_geom_type).status = 'latest' -- excludes deleted
        -- ohsome-filter-to-sql generated clause
        AND ($filter)
        AND ST_Intersects(c.geom, ST_GeomFromGeoJSON($geom))
    GROUP BY
        month
)
SELECT
    Date_trunc('month', serie.month) as month,
    COALESCE(contribution, 0) as contribution
FROM
    -- Filling monthly gaps (no data) with 0
    serie LEFT JOIN contribution ON (serie.month = contribution.month)
ORDER BY
    month;
