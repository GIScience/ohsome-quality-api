from typing import Optional

from schema import Optional as Opt
from schema import Or, Schema


def generate_properties_template(iterator: Optional[str] = None) -> dict:
    properties = {
        "metadata.name": str,
        "metadata.description": str,
        "layer.name": str,
        "layer.description": str,
        "result.timestamp_oqt": str,
        "result.timestamp_osm": Or(str, None),
        "result.value": Or(float, None),
        "result.label": str,
        "result.description": str,
        "result.svg": str,
    }

    if iterator is None:
        return properties.copy()
    else:
        return {str(iterator) + "." + k: v for k, v in properties.items()}


def get_report_properties_template() -> dict:
    return {
        "metadata.name": str,
        "metadata.description": str,
        "result.value": float,
        "result.label": str,
        "result.description": str,
    }


def get_response_schema() -> Schema:
    return Schema(
        {
            "apiVersion": str,
            "attribution": {
                "text": str,
                "url": str,
            },
            "requestUrl": str,
        },
        ignore_extra_keys=True,
    )


def get_feature_schema(iterator: Optional[str] = None):
    return Schema(
        {
            "type": "Feature",
            "geometry": dict,
            Opt("id"): Or(str, int),
            "properties": generate_properties_template(iterator),
        },
        ignore_extra_keys=True,
    )


def get_featurecollection_schema():
    return Schema(
        {"type": "FeatureCollection", "features": list}, ignore_extra_keys=True
    )
