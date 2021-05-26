INSERT INTO results (
    indicator,
    layer,
    dataset,
    id,
    timestamp_oqt,
    timestamp_osm,
    label,
    value,
    description,
    svg)
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
    $10)
ON CONFLICT (
    indicator,
    layer,
    dataset,
    id)
    DO UPDATE SET
        (
            timestamp_oqt,
            timestamp_osm,
            label,
            value,
            description,
            svg) = (
            excluded.timestamp_oqt,
            excluded.timestamp_osm,
            excluded.label,
            excluded.value,
            excluded.description,
            excluded.svg);
