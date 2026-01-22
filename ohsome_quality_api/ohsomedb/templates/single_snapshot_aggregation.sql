WITH poly AS (
    SELECT ST_GeomFromGeoJSON(${{ geom }}) AS geom
)
SELECT
    NOW()::timestamp AS snapshot_ts,
    {% if aggregation == 'length' %}
        SUM(
            CASE
                WHEN ST_Within(c.geom, p.geom)
                THEN c.length -- Use precomputed length from ohsome-planet
                ELSE ST_Length(ST_Intersection(c.geom, p.geom))
            END
        )::BIGINT AS value
    {% elif aggregation == 'area' or aggregation == 'area\density' %}
        SUM(
            CASE
                WHEN ST_Within(c.geom, p.geom)
                THEN c.area -- Use precomputed area from ohsome-planet
                ELSE ST_Area(ST_Intersection(c.geom, p.geom))
            END
        )::BIGINT AS value
    {% else %}
        COUNT(*) AS value
    {% endif %}
FROM {{ contributions }} c, poly AS p
WHERE 1=1
    AND (status_geom_type).status IN ('latest')
    AND valid_to >= NOW()::timestamp
    AND valid_from < NOW()::timestamp  -- before last snapshot time
    AND ({{ filter }})
    AND ST_Intersects(c.geom, p.geom);
