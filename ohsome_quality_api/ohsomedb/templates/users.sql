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
user_count AS (
    SELECT
        Date_trunc('month', c.valid_from) AS month,
        COUNT(DISTINCT c.user_id) AS user_count
    FROM
        {{ contributions }} c
    WHERE 1=1
        -- TODO: this would be more performant but ohsome-filter-to-sql can not generate this
        -- clause because is does not know about "latest"
        -- AND status_geom_type = ANY(ARRAY[('latest', 'Polygon'), ('latest', 'MultiPolygon')]::_status_geom_type_type)
        -- ohsome-filter-to-sql generated clause
        AND ({{ filter }})
        AND ST_Intersects(c.geom, ST_GeomFromGeoJSON(${{ geom }}))
    GROUP BY
        month
)
SELECT
    Date_trunc('month', serie.month) as month,
    COALESCE(user_count, 0) as "user"
FROM
    -- Filling monthly gaps (no data) with 0
    serie LEFT JOIN user_count ON (serie.month = user_count.month)
ORDER BY
    month;
