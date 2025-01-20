from dataclasses import dataclass

from geojson import Feature
from geojson.utils import coords
from pyproj import Geod


@dataclass
class BoundingBox:
    lon_min: float  # left
    lat_min: float  # bottom
    lon_max: float  # right
    lat_max: float  # top


def get_coordinates(feature: Feature) -> tuple:
    coordinates = tuple(coords(feature))
    lons = tuple(c[0] for c in coordinates)
    lats = tuple(c[1] for c in coordinates)
    return lons, lats


def calculate_area(feature: Feature) -> float:
    """Calculate area in meter."""
    lons, lats = get_coordinates(feature)
    geod = Geod(ellps="WGS84")
    area, _ = geod.polygon_area_perimeter(lons=lons, lats=lats)
    return area


def get_bounding_box(feature: Feature) -> BoundingBox:
    lons, lats = get_coordinates(feature)
    return BoundingBox(
        lon_min=min(lons),
        lat_min=min(lats),
        lon_max=max(lons),
        lat_max=max(lats),
    )
