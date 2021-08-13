import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
from ohsome_quality_analyst.utils.definitions import configure_logging

configure_logging()
logging.info("Logging enabled")
logging.debug("Debugging output enabled")

app = FastAPI(
    title="OQT API",
    description="Intrinsic and extrinsic data quality metrics for OpenStreetMap data.",
    version=oqt_version,
    contact={
        "name": "ohsome team",
        "url": "https://oqt.ohsome.org/",
        "email": "ohsome@heigit.org",
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def empty_api_response() -> dict:
    return {
        "apiVersion": oqt_version,
        "attribution": {
            "text": "© OpenStreetMap contributors",
            "url": "https://ohsome.org/copyrights",
        },
    }


@app.get("/indicator/{name}")
async def get_indicator(
    name: IndicatorEnum,
    layerName: LayerEnum,  # noqa N803
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
        fidField = fidField.value  # noqa N806
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
    fid_field = p.get("fid_field", None)
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value
    return await _fetch_indicator(
        name.value,
        p["layer_name"].value,
        p["bpolys"],
        dataset,
        p["feature_id"],
        fid_field,
    )


async def _fetch_indicator(
    name: str,
    layer_name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
) -> dict:
    geojson_object = await oqt.create_indicator_as_geojson(
        name,
        layer_name,
        bpolys,
        dataset,
        feature_id,
        fid_field,
        size_restriction=True,
    )
    response = empty_api_response()
    response.update(geojson_object)
    return response


@app.get("/report/{name}")
async def get_report(
    name: ReportEnum,
    bpolys: Optional[str] = None,
    dataset: Optional[DatasetEnum] = None,
    featureId: Optional[str] = None,  # noqa N803
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
        fidField = fidField.value  # noqa N806
    return await _fetch_report(name.value, bpolys, dataset, featureId, fidField)


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
    fid_field = p["fid_field"]
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value

    return await _fetch_report(
        name.value,
        p["bpolys"],
        dataset,
        p["feature_id"],
        fid_field,
    )


async def _fetch_report(
    name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
    fid_field: Optional[str] = None,
):
    geojson_object = await oqt.create_report_as_geojson(
        name,
        bpolys=bpolys,
        dataset=dataset,
        feature_id=feature_id,
        fid_field=fid_field,
        size_restriction=True,
    )
    response = empty_api_response()
    response.update(geojson_object)
    return response


@app.get("/regions")
async def get_available_regions():
    return await db_client.get_available_regions()
