CREATE TABLE IF NOT EXISTS results (
    indicator_name text,  -- INDICATOR is a SQL keyword
    layer_key text,
    dataset_name text,
    fid text,
    timestamp_oqt timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    timestamp_osm timestamp with time zone,
    result_label text,
    result_value float,  -- VALUE is an SQL keyword
    result_description text,
    result_svg text,
    feature json,
    PRIMARY KEY (indicator_name, layer_key, dataset_name, fid)
);
