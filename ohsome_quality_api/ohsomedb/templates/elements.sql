-- Parsing the GeoJSON directly in the WHERE clause instead of
-- in a WITH clause makes the query faster
WITH bpoly AS (
    SELECT ST_GeomFromGeoJSON (${{ geom }}) AS geom
),
series AS (
    SELECT
        Generate_series(
            '2007-10-01'::timestamp,
            contributions_state.last_timestamp::timestamp,
            '1 month'::interval
        ) AS ts
    FROM contributions_state
),
stats AS (
    SELECT
        {% if aggregation == 'length' %}
            SUM(
                CASE
                    WHEN ST_Within(
                        c.geom,
                        b.geom
                    )
                    THEN c.length -- Use precomputed area from ohsome-planet
                    ELSE ST_Length(
                        ST_Intersection(
                            c.geom,
                            b.geom
                        )::geography
                    )
                END
            )::BIGINT
        {% elif aggregation == 'area' or aggregation == 'area\density' %}
            SUM(
                CASE
                    WHEN ST_Within(
                        c.geom,
                        b.geom,
                    )
                    THEN c.area -- Use precomputed area from ohsome-planet
                    ELSE ST_Area(
                        ST_Intersection(
                            c.geom,
                            b.geom,
                        )::geography
                    )
                END
            )::BIGINT
        {% else %}
            COUNT(*)
        {% endif %}
            AS element,
        s.ts
    FROM {{ contributions }} c, series s, bpoly b
    WHERE 1=1
        -- ohsome-filter-to-sql generated clause
        AND ({{ filter }})
        -- include only valid stat (exclude states such as deleted and invalid)
        AND (status_geom_type).status in ('history', 'latest')
        AND ST_Intersects(c.geom, b.geom)
        AND c.valid_from <= s.ts AND s.ts < c.valid_to
    GROUP BY ts
   )
SELECT
    series.ts AS timestamp,
    COALESCE(stats.element, 0) AS element
FROM
    series LEFT JOIN stats ON series.ts = stats.ts
ORDER BY timestamp;
