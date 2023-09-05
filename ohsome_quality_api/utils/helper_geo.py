import logging

from pyproj import Geod

from ohsome_quality_api.api.request_models import Feature


def calculate_area(feature: Feature) -> float:
    """Calculate area in meter."""
    geod = Geod(ellps="WGS84")
    if feature.geometry.type == "Polygon":
        coordinates = feature.geometry.__geo_interface__.get("coordinates")
    else:
        coordinates = [
            polygon[0]
            for polygon in feature.geometry.__geo_interface__.get("coordinates")
        ]

    area = 0
    for polygon in coordinates:
        lons = tuple(c[0] for c in polygon)
        lats = tuple(c[1] for c in polygon)
        area += geod.polygon_area_perimeter(lons=lons, lats=lats)[0]
    return area


def reproject_polygon_or_multi_polygon(func, obj):
    """Reproject (Multi)-Polygons to new CRS with passable func."""
    if obj["type"] == "Polygon":
        coordinates = [[tuple(func(c)) for c in curve] for curve in obj["coordinates"]]
    elif obj["type"] == "MultiPolygon":
        coordinates = [
            [[tuple(func(c)) for c in curve] for curve in part]
            for part in obj["coordinates"]
        ]
    else:
        logging.debug("Non Polygon Type detected")
    return {"type": obj["type"], "coordinates": coordinates}


def reproject_feature_or_feature_collection(func, obj):
    """Reproject Feature(Collection)s to new CRS with passable func."""
    if obj["type"] == "Feature":
        obj["geometry"] = (
            reproject_polygon_or_multi_polygon(func, obj["geometry"])
            if obj["geometry"]
            else None
        )
        return obj
    elif obj["type"] == "FeatureCollection":
        feats = [
            reproject_feature_or_feature_collection(func, feat)
            for feat in obj["features"]
        ]
        return {"type": obj["type"], "features": feats}
