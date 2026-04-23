-- Parsing the GeoJSON directly in the WHERE clause instead of
-- in a WITH clause makes the query faster
with stats AS (
    SELECT
        {% if aggregation == 'length' %}
            0.001 * SUM(
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
            0.001 * 0.001 * SUM(
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
        AS aggregation,
        {{ attribute_filter }} has_attribute
    FROM
        {{ contributions }} c
    WHERE 1=1
        -- TODO: this would be more performant but ohsome-filter-to-sql can not generate this
        -- clause because is does not know about "latest"
        -- AND status_geom_type = ANY(ARRAY[('latest', 'Polygon'), ('latest', 'MultiPolygon')]::_status_geom_type_type)
        AND (status_geom_type).status = 'latest' -- excludes deleted
        -- ohsome-filter-to-sql generated clause
        AND ({{ filter }})
        AND ST_Intersects(c.geom, ST_GeomFromGeoJSON(${{ geom }}))
    GROUP BY has_attribute
)
SELECT
    COALESCE(SUM(aggregation), 0) AS total_aggregation,
    COALESCE(SUM(aggregation) FILTER (WHERE has_attribute), 0) AS aggregation_with_attribute,
    COALESCE(
        SUM(aggregation) FILTER (WHERE has_attribute)
        / NULLIF(SUM(aggregation), 0)::float,
        0
    ) AS attribute_completeness
FROM stats;
