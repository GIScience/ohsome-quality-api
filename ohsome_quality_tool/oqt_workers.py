import geojson

from ohsome_quality_tool.utils.config import POSTGRES_DB
from ohsome_quality_tool.utils.definitions import Indicators, logger

logger.info("hello")

print(f"postgres db name: {POSTGRES_DB}")


bpolys = geojson.loads(
    """{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {},
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
              8.674092292785645,
              49.40427147224242
            ],
            [
              8.695850372314453,
              49.40427147224242
            ],
            [
              8.695850372314453,
              49.415552187316095
            ],
            [
              8.674092292785645,
              49.415552187316095
            ],
            [
              8.674092292785645,
              49.40427147224242
            ]
          ]
        ]
      }
    }
  ]
}"""
)


indicator = Indicators.BUILDING_COMPLETENESS.constructor(bpolys=bpolys)
indicator.run()
