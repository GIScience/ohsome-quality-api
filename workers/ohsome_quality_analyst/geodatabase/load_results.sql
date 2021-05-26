SELECT
    indicator,
    layer,
    dataset,
    fid,
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
    AND fid = $4
