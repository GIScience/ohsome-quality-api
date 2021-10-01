SELECT
    row_to_json(feature_collection)
FROM (
    SELECT
        'FeatureCollection' AS "type",
        array_to_json(array_agg(feature)) AS "features"
    FROM (
        SELECT
            'Feature' AS "type",
            (
                SELECT
                    json_strip_nulls(row_to_json(t))
                FROM (
                    SELECT
                        ogc_fid as id,
                        name
                ) AS t
            ) AS "properties"
        FROM
            regions
    ) AS feature
) AS feature_collection
