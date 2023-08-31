from geojson_pydantic import Feature
from pyproj import Geod


def calculate_area(feature: Feature) -> float:
    """Calculate area in meter."""
    geod = Geod(ellps="WGS84")
    coordinates = feature.geometry.__geo_interface__.get("coordinates")[0]
    lons = tuple(c[0] for c in coordinates)
    lats = tuple(c[1] for c in coordinates)
    area, _ = geod.polygon_area_perimeter(lons=lons, lats=lats)
    return area
