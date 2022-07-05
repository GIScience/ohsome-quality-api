INSERT INTO results (
    indicator_name,
    layer_key,
    dataset_name,
    fid,
    timestamp_oqt,
    timestamp_osm,
    result_class,
    result_value,
    result_description,
    result_svg,
    feature)
VALUES (
    $1,
    $2,
    $3,
    $4,
    $5,
    $6,
    $7,
    $8,
    $9,
    $10,
    $11)
ON CONFLICT (
    indicator_name,
    layer_key,
    dataset_name,
    fid)
    DO UPDATE SET
        (
            timestamp_oqt,
            timestamp_osm,
            result_class,
            result_value,
            result_description,
            result_svg,
            feature) = (
            excluded.timestamp_oqt,
            excluded.timestamp_osm,
            excluded.result_class,
            excluded.result_value,
            excluded.result_description,
            excluded.result_svg,
            excluded.feature);
