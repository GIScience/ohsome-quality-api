SELECT
    indicator,
    layer,
    dataset,
    id,
    timestamp_oqt,
    timestamp_osm,
    label,
    value,
    description,
    svg
FROM
    results
WHERE
    indicator = $1
    AND layer = $2
    AND dataset = $3
    AND id = $4
