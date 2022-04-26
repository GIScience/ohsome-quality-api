SELECT
    json_build_object('type', 'FeatureCollection', 'features', json_agg(feature))
FROM
    results;
