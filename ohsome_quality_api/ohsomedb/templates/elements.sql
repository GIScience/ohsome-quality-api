-- Parsing the GeoJSON directly in the WHERE clause instead of
-- in a WITH clause makes the query faster
WITH serie AS (
    SELECT
        Generate_series(
            '2007-10-01'::timestamp,
            NOW()::timestamp,
            '1 month'::interval
        ) AS ts
)
SELECT
    {% if aggregation == 'length' %}
        SUM(
            CASE
                WHEN ST_Within(
                    c.geom,
                    ST_GeomFromGeoJSON(${{ geom }})
                )
                THEN c.length -- Use precomputed area from ohsome-planet
                ELSE ST_Length(
                    ST_Intersection(
                        c.geom,
                        ST_GeomFromGeoJSON(${{ geom }})
                    )::geography
                )
            END
        )::BIGINT
    {% elif aggregation == 'area' or aggregation == 'area\density' %}
        SUM(
            CASE
                WHEN ST_Within(
                    c.geom,
                    ST_GeomFromGeoJSON(${{ geom }})
                )
                THEN c.area -- Use precomputed area from ohsome-planet
                ELSE ST_Area(
                    ST_Intersection(
                        c.geom,
                        ST_GeomFromGeoJSON(${{ geom }})
                    )::geography
                )
            END
        )::BIGINT
    {% else %}
        COUNT(*)
    {% endif %}
        AS element
FROM {{ contributions }} c, serie s
WHERE 1=1
    -- ohsome-filter-to-sql generated clause
    AND ({{ filter }})
    AND ST_Intersects(c.geom, ST_GeomFromGeoJSON(${{ geom }}))
    AND c.valid_from <= s.ts AND s.ts < c.valid_to
GROUP BY ts
ORDER BY ts;
