"""This module defines schemata for API responses.

Every API response must adhere to the general schema.
Additionally, API responses need to adhere to one additional schema depending on which
endpoint is used.
"""

from schema import Optional as Opt
from schema import Or, Schema


def get_indicator_properties_template():
    return {
        "metadata": {
            "name": str,
            "description": str,
        },
        "layer": {
            "name": str,
            "description": str,
        },
        "result": {
            "timestamp_oqt": str,
            "timestamp_osm": Or(str),
            "value": Or(float, str, int, None),
            "label": str,
            "description": str,
            Opt("svg"): str,
        },
    }


def get_general_schema() -> Schema:
    """General response schema.

    Every response should have this schema
    """
    return Schema(
        {
            "apiVersion": str,
            "attribution": {
                "url": str,
                Opt("text"): str,
            },
        },
        ignore_extra_keys=True,
    )


def get_result_schema() -> Schema:
    """Response schema for all endpoints.

    Excluded are the endpoints `/indicator` and `/report`.
    """
    return Schema({"result": list}, ignore_extra_keys=True)


def get_featurecollection_schema() -> Schema:
    """Response schema for responses of type FeatureCollection"""
    return Schema(
        {"type": "FeatureCollection", "features": list}, ignore_extra_keys=True
    )


def get_indicator_feature_schema() -> Schema:
    properties = get_indicator_properties_template()
    return Schema(
        {
            "type": "Feature",
            "geometry": dict,
            Opt("id"): Or(str, int),
            "properties": properties,
        },
        ignore_extra_keys=True,
    )


def get_report_feature_schema(number_of_indicators: int) -> Schema:
    schema = Schema(
        {
            "type": "Feature",
            "geometry": dict,
            Opt("id"): Or(str, int),
            "properties": {
                "report": {
                    "metadata": {
                        "name": str,
                        "description": str,
                    },
                    "result": {
                        "value": float,
                        "label": str,
                        "description": str,
                    },
                },
                "indicators": [get_indicator_properties_template()],
            },
        },
        ignore_extra_keys=True,
    )
    return schema
