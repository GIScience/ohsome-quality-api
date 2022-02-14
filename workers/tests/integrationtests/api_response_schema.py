"""This module defines schemata for API responses.

Every API response must adhere to the general schema.
Additionally, API responses need to adhere to one additional schema depending on which
endpoint is used.
"""

from schema import Optional as Opt
from schema import Or, Schema


def get_indicator_properties_template():
    return {
        "metadata.name": str,
        "metadata.description": str,
        "layer.name": str,
        "layer.description": str,
        "result.timestamp_oqt": str,
        "result.timestamp_osm": Or(str),
        "result.value": Or(float, None),
        "result.label": str,
        "result.description": str,
        Opt("result.svg"): str,
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
    properties_template = get_indicator_properties_template()
    properties = {}
    for i in range(number_of_indicators):
        for k, v in properties_template.items():
            prefix = "indicators." + str(i) + "."
            if isinstance(k, Schema):
                k._prepend_schema_name(prefix)
            else:
                k = prefix + k
            properties.update({k: v})
    schema = Schema(
        {
            "type": "Feature",
            "geometry": dict,
            Opt("id"): Or(str, int),
            "properties": {
                "report.metadata.name": str,
                "report.metadata.description": str,
                "report.result.value": float,
                "report.result.label": str,
                "report.result.description": str,
                **properties,
            },
        },
        ignore_extra_keys=True,
    )
    return schema
