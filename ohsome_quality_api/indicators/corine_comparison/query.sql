SELECT
    CASE
        WHEN ST_Within(
            geometry,
            ST_MakeEnvelope(
                CAST({xmin} AS DOUBLE),
                CAST({ymin} AS DOUBLE),
                CAST({xmax} AS DOUBLE),
                CAST({ymax} AS DOUBLE)
            )
        ) THEN area
        ELSE ST_Intersection(
            geometry,
            ST_MakeEnvelope(
                CAST({xmin} AS DOUBLE),
                CAST({ymin} AS DOUBLE),
                CAST({xmax} AS DOUBLE),
                CAST({ymax} AS DOUBLE)
            )
        ).ST_FlipCoordinates().ST_Area_Spheroid()
    END as area
    FROM corine_osm_intersection
    WHERE ST_Intersects(
        geometry,
        ST_MakeEnvelope(
            CAST({xmin} AS DOUBLE),
            CAST({ymin} AS DOUBLE),
            CAST({xmax} AS DOUBLE),
            CAST({ymax} AS DOUBLE)
        )
    )