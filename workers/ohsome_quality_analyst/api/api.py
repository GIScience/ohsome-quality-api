import logging
from typing import Optional

import geojson
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from geojson import Feature, FeatureCollection, MultiPolygon, Polygon

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.api.request_models import (
    DatasetEnum,
    FidFieldEnum,
    IndicatorEnum,
    IndicatorRequestModel,
    LayerEnum,
    ReportEnum,
    ReportRequestModel,
)
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.definitions import GEOM_SIZE_LIMIT, configure_logging
from ohsome_quality_analyst.utils.helper import name_to_lower_camel

configure_logging()
logging.info("Logging enabled")
logging.debug("Debugging output enabled")

app = FastAPI(title="OQT API", description="https://oqt.ohsome.org/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def empty_api_response() -> dict:
    return {
        "attribution": {
            "url": "https://ohsome.org/copyrights",
            "text": "© OpenStreetMap contributors",
        },
        "apiVersion": oqt_version,
    }


async def load_bpolys(bpolys: str) -> Feature:
    """Load as GeoJSON object, validate and check size of bpolys"""

    async def check_geom_size(geom):
        if await db_client.get_area_of_bpolys(geom) > GEOM_SIZE_LIMIT:
            raise ValueError(
                "Input GeoJSON Object is too big. "
                + "The area should be less than {0} sqkm.".format(GEOM_SIZE_LIMIT)
            )

    bpolys = geojson.loads(bpolys)

    if bpolys.is_valid is False:
        raise ValueError("Input geometry is not valid")
    elif isinstance(bpolys, FeatureCollection):
        if len(bpolys.features) == 1:
            feature = bpolys.features[0]
            await check_geom_size(feature.geometry)
            return feature
        else:
            raise ValueError("Only one Feature is supported in a FeatureCollection")
    elif isinstance(bpolys, Feature):
        await check_geom_size(bpolys.geometry)
        return bpolys
    elif isinstance(bpolys, (Polygon, MultiPolygon)):
        await check_geom_size(bpolys)
        return Feature(geometry=bpolys)
    else:
        raise ValueError(
            "Input GeoJSON Objects have to be of type Feature, Polygon or MultiPolygon"
        )


@app.get("/indicator/{name}")
async def get_indicator(
    name: IndicatorEnum,
    layerName: LayerEnum,
    bpolys: Optional[str] = None,
    dataset: Optional[DatasetEnum] = None,
    featureId: Optional[str] = None,
    fidField: Optional[FidFieldEnum] = None,
):
    """Create an Indicator.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved.
    """
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        fidField = fidField.value
    return await _fetch_indicator(
        name.value, layerName.value, bpolys, dataset, featureId, fidField
    )


@app.post("/indicator/{name}")
async def post_indicator(
    name: IndicatorEnum,
    parameters: IndicatorRequestModel,
):
    """Create an Indicator.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved.
    """
    p = parameters.dict()
    dataset = p["dataset"]
    fidField = p["fidField"]
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        fidField = fidField.value
    return await _fetch_indicator(
        name.value,
        p["layerName"].value,
        p["bpolys"],
        dataset,
        p["featureId"],
        fidField,
    )


async def _fetch_indicator(
    name: str,
    layer_name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
):
    if bpolys is not None:
        feature = await load_bpolys(bpolys)
    else:
        feature = None

    indicator = await oqt.create_indicator(
        name, layer_name, feature, dataset, feature_id, fid_field
    )

    response = empty_api_response()
    response["metadata"] = vars(indicator.metadata)
    response["metadata"].pop("result_description", None)
    response["metadata"].pop("label_description", None)
    response["layer"] = vars(indicator.layer)
    response["result"] = vars(indicator.result)
    return response


@app.get("/report/{name}")
async def get_report(
    name: ReportEnum,
    bpolys: Optional[str] = None,
    dataset: Optional[DatasetEnum] = None,
    featureId: Optional[str] = None,
    fidField: Optional[FidFieldEnum] = None,
):
    """Create a Report.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved.
    """
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        fidField = fidField.value
    return await _fetch_report(
        name.value,
        bpolys,
        dataset,
        featureId,
        fidField,
    )


@app.post("/report/{name}")
async def post_report(name: ReportEnum, parameters: ReportRequestModel):
    """Create a Report.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved.
    """
    p = parameters.dict()
    dataset = p["dataset"]
    fidField = p["fidField"]
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        fidField = fidField.value

    return await _fetch_report(
        name.value,
        p["bpolys"],
        dataset,
        p["featureId"],
        fidField,
    )


async def _fetch_report(
    name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
):
    if bpolys is not None:
        feature = await load_bpolys(bpolys)
    else:
        feature = None

    report = await oqt.create_report(
        name,
        feature=feature,
        dataset=dataset,
        feature_id=feature_id,
        fid_field=fid_field,
    )

    response = empty_api_response()
    response["metadata"] = vars(report.metadata)
    response["metadata"].pop("label_description", None)
    response["result"] = vars(report.result)
    response["result"]["label"] = report.result.label
    response["indicators"] = {}
    for indicator in report.indicators:
        metadata = vars(indicator.metadata)
        metadata.pop("result_description", None)
        metadata.pop("label_description", None)
        layer = vars(indicator.layer)
        result = vars(indicator.result)
        indicator_name = name_to_lower_camel(metadata["name"])
        layer_name = name_to_lower_camel(layer["name"])
        response["indicators"][indicator_name + layer_name] = {
            "metadata": metadata,
            "layer": layer,
            "result": result,
        }
    return response


@app.get("/regions")
async def get_available_regions():
    return await db_client.get_available_regions()
