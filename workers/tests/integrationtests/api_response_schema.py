"""This module defines schemata for API responses.

One API response should adhere to at least two schemata.
It should always adhere to the general schema.
"""

from typing import Optional

from schema import Optional as Opt
from schema import Or, Schema


def generate_properties_template(iterator: Optional[str] = None) -> dict:
    raise NotImplementedError


def get_general_schema() -> Schema:
    """General response schema.

    Every response should have this schema
    """
    return Schema(
        {
            "apiVersion": str,
            "attribution": {
                "text": str,
                "url": str,
            },
        },
        ignore_extra_keys=True,
    )


def get_result_schema() -> Schema:
    """Response schema for all endpoints except of 'indicator' and 'report' endpoints"""
    return Schema({"result": list}, ignore_extra_keys=True)


def get_featurecollection_schema() -> Schema:
    """Response schema for responses of type FeatureCollection"""
    return Schema(
        {"type": "FeatureCollection", "features": list}, ignore_extra_keys=True
    )


def get_indicator_feature_schema() -> Schema:
    return Schema(
        {
            "type": "Feature",
            "geometry": dict,
            Opt("id"): Or(str, int),
            "properties": {
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
            },
        },
        ignore_extra_keys=True,
    )


def get_report_feature_schema(number_of_indicators: int) -> Schema:
    properties_template = {
        "metadata.name": str,
        "metadata.description": str,
        "layer.name": str,
        "layer.description": str,
        "result.timestamp_oqt": str,
        "result.timestamp_osm": Or(str),
        "result.value": Or(float, None),
        "result.label": str,
        "result.description": str,
        "result.svg": str,
    }
    properties = {}
    for i in range(number_of_indicators):
        for k, v in properties_template.items():
            if k == "result.svg":
                properties.update({Opt("indicators." + str(i) + "." + k): v})
            else:
                properties.update({"indicators." + str(i) + "." + k: v})
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
