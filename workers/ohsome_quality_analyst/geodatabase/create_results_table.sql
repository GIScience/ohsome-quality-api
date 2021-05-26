CREATE TABLE IF NOT EXISTS results (
    indicator text,
    layer text,
    dataset text,
    id text,
    timestamp_oqt timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    timestamp_osm timestamp with time zone,
    label text,
    value float,
    description text,
    svg text,
    PRIMARY KEY (indicator, layer, dataset, id)
);
