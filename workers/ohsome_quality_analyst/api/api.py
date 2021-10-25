import json
import logging
from typing import Optional, Union

import pydantic
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ohsome_quality_analyst import (
    __author__,
    __description__,
    __email__,
    __homepage__,
    __title__,
    __version__,
    oqt,
)
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
from ohsome_quality_analyst.utils.definitions import (
    INDICATOR_LAYER,
    configure_logging,
    get_dataset_names_api,
    get_fid_fields_api,
    get_indicator_names,
    get_layer_names,
    get_report_names,
)
from ohsome_quality_analyst.utils.exceptions import OhsomeApiError, SizeRestrictionError

MEDIA_TYPE_GEOJSON = "application/geo+json"

configure_logging()
logging.info("Logging enabled")
logging.debug("Debugging output enabled")

app = FastAPI(
    title=__title__,
    description=__description__,
    version=__version__,
    contact={
        "name": __author__,
        "url": __homepage__,
        "email": __email__,
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exception: RequestValidationError
):
    """Override request validation exceptions.

    `pydantic` raises on exception regardless of the number of errors found.
    The `ValidationError` will contain information about all the errors.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "apiVersion": __version__,
                "detail": exception.errors(),
                "type": "RequestValidationError",
            },
        ),
    )


@app.exception_handler(OhsomeApiError)
@app.exception_handler(SizeRestrictionError)
async def oqt_exception_handler(
    request: Request, exception: Union[OhsomeApiError, SizeRestrictionError]
):
    """Exception handler for custom OQT exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "apiVersion": __version__,
            "detail": exception.message,
            "type": exception.name,
        },
    )


def empty_api_response() -> dict:
    return {
        "apiVersion": __version__,
        "attribution": {
            "text": "© OpenStreetMap contributors",
            "url": "https://ohsome.org/copyrights",
        },
    }


@app.get("/indicator")
async def get_indicator(
    name: IndicatorEnum,
    layerName: LayerEnum,
    bpolys: Optional[str] = None,
    dataset: Optional[DatasetEnum] = None,
    featureId: Optional[str] = None,
    fidField: Optional[FidFieldEnum] = None,
):
    """Create an Indicator.

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    if bpolys is not None:
        bpolys = json.loads(bpolys)
    raw = {
        "name": name,
        "layerName": layerName,
        "bpolys": bpolys,
        "dataset": dataset,
        "featureId": featureId,
        "fidField": fidField,
    }
    parameters = {k: v for k, v in raw.items() if v is not None}
    return await _fetch_indicator(parameters)


@app.post("/indicator")
async def post_indicator(
    parameters: IndicatorRequestModel,
):
    """Create an Indicator.

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    return await _fetch_indicator(parameters)


@pydantic.validate_arguments
async def _fetch_indicator(
    parameters: IndicatorRequestModel,
) -> dict:
    p = parameters.dict()
    dataset = p["dataset"]
    fid_field = p["fid_field"]
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value
    geojson_object = await oqt.create_indicator_as_geojson(
        p["name"].value,
        p["layer_name"].value,
        p["bpolys"],
        dataset,
        p["feature_id"],
        fid_field,
        size_restriction=True,
    )
    response = empty_api_response()
    response.update(geojson_object)
    return JSONResponse(
        content=jsonable_encoder(response), media_type=MEDIA_TYPE_GEOJSON
    )


@app.get("/report")
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
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    if bpolys is not None:
        bpolys = json.loads(bpolys)
    raw = {
        "name": name,
        "bpolys": bpolys,
        "dataset": dataset,
        "featureId": featureId,
        "fidField": fidField,
    }
    parameters = {k: v for k, v in raw.items() if v is not None}
    return await _fetch_report(parameters)


@app.post("/report")
async def post_report(parameters: ReportRequestModel):
    """Create a Report.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    return await _fetch_report(parameters)


@pydantic.validate_arguments
async def _fetch_report(parameters: ReportRequestModel):
    p = parameters.dict()
    dataset = p["dataset"]
    fid_field = p["fid_field"]
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value
    geojson_object = await oqt.create_report_as_geojson(
        p["name"].value,
        bpolys=p["bpolys"],
        dataset=dataset,
        feature_id=p["feature_id"],
        fid_field=fid_field,
        size_restriction=True,
    )
    response = empty_api_response()
    response.update(geojson_object)
    return JSONResponse(
        content=jsonable_encoder(response), media_type=MEDIA_TYPE_GEOJSON
    )


@app.get("/regions")
async def get_available_regions(asGeoJSON: bool = False):
    """Get regions as list of names and identifiers or as GeoJSON.

    Args:
        asGeoJSON: If `True` regions will be returned as GeoJSON
    """
    response = empty_api_response()
    if asGeoJSON is True:
        regions = await db_client.get_regions_as_geojson()
        response.update(regions)
        return JSONResponse(
            content=jsonable_encoder(response), media_type=MEDIA_TYPE_GEOJSON
        )
    else:
        response["result"] = await db_client.get_regions()
        return response


@app.get("/indicatorLayerCombinations")
async def list_indicator_layer_combinations():
    """List names of available indicator-layer-combinations."""
    response = empty_api_response()
    response["result"] = INDICATOR_LAYER
    return response


@app.get("/indicatorNames")
async def list_indicators():
    """List names of available indicators."""
    response = empty_api_response()
    response["result"] = get_indicator_names()
    return response


@app.get("/datasetNames")
async def list_datasets():
    """List names of available datasets."""
    response = empty_api_response()
    response["result"] = get_dataset_names_api()
    return response


@app.get("/layerNames")
async def list_layers():
    """List names of available layers."""
    response = empty_api_response()
    response["result"] = get_layer_names()
    return response


@app.get("/reportNames")
async def list_reports():
    """List names of available reports."""
    response = empty_api_response()
    response["result"] = get_report_names()
    return response


@app.get("/FidFields")
async def list_fid_fields():
    """List available fid fields for each dataset."""
    response = empty_api_response()
    response["result"] = get_fid_fields_api()
    return response
