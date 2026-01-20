WITH series AS (SELECT generate_series('2007-10-01'::timestamp,
            NOW()::timestamp, 'P1M'::interval) AS ts),
poly AS (
    SELECT ST_GeomFromGeoJSON(${{ geom }}) AS geom
)
SELECT
    ts AS timestamp,
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
        AS value
FROM series JOIN {{ contributions }} c ON (valid_from <= ts AND ts < valid_to) CROSS JOIN poly p
WHERE 1=1
    -- TODO: this would be more performant but ohsome-filter-to-sql can not generate this
    -- clause because is does not know about "latest"
    -- AND status_geom_type = ANY(ARRAY[('history','LineString')::status_geom_type_type, ('latest','LineString')::status_geom_type_type])
    -- ohsome-filter-to-sql generated clause
    AND ({{ filter }})
    AND ST_Intersects(c.geom, p.geom)
GROUP BY ts
ORDER BY ts
;
