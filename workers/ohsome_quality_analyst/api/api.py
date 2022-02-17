import fnmatch
import json
import logging
from typing import Union

from fastapi import Body, Depends, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from geojson import Feature, FeatureCollection
from pydantic import ValidationError

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
    INDICATOR_EXAMPLES,
    REPORT_EXAMPLES,
    IndicatorBpolys,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
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
from ohsome_quality_analyst.utils.exceptions import (
    OhsomeApiError,
    RasterDatasetNotFoundError,
    RasterDatasetUndefinedError,
    SizeRestrictionError,
)
from ohsome_quality_analyst.utils.helper import json_serialize

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


class CustomJSONResponse(JSONResponse):
    def render(self, content):
        return json.dumps(content, default=json_serialize).encode()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exception: Union[RequestValidationError, ValidationError]
):
    """Override request validation exceptions.

    `pydantic` raises on exception regardless of the number of errors found.
    The `ValidationError` will contain information about all the errors.

    FastAPIs `RequestValidationError` is a subclass of pydantic's `ValidationError`.
    Because of the usage of `@pydantic.validate_arguments` decorator
    `ValidationError` needs to be specified in this handler as well.
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
    request: Request,
    exception: Union[
        OhsomeApiError,
        SizeRestrictionError,
        RasterDatasetNotFoundError,
        RasterDatasetUndefinedError,
    ],
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
            "text": (
                "© OpenStreetMap contributors;"
                "© European Union, 1995-2022"
                "Global Human Settlement Layer Data;"
                "Earth Observation Group Nighttime Light Data."
            ),
            "url": (
                "https://github.com/GIScience/ohsome-quality-analyst/blob/main/data/"
                "LICENSES.md"
            ),
        },
    }


@app.get("/indicator")
async def get_indicator(parameters=Depends(IndicatorDatabase)):
    """Request an already calculated Indicator for an AOI defined by OQT.

    The response is a GeoJSON Feature with the indicator results as properties.
    To request an Indicator for a custom AOI please use the POST method.
    """
    return await _fetch_indicator(parameters)


@app.post("/indicator")
async def post_indicator(
    parameters: Union[IndicatorBpolys, IndicatorDatabase] = Body(
        ...,
        examples=INDICATOR_EXAMPLES,
    )
):
    """Request an Indicator for an AOI defined by OQT or a custom AOI.

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or FeatureCollection with
    the indicator results. The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    return await _fetch_indicator(parameters)


async def _fetch_indicator(parameters) -> CustomJSONResponse:
    p = parameters.dict()
    dataset = p.get("dataset", None)
    fid_field = p.get("fid_field", None)
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value
    geojson_object = await oqt.create_indicator_as_geojson(
        p["name"].value,
        p["layer_name"].value,
        p.get("bpolys", None),
        dataset,
        p.get("feature_id", None),
        fid_field,
        size_restriction=True,
    )
    if p["include_svg"] is False:
        remove_svg_from_properties(geojson_object)
    response = empty_api_response()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.get("/report")
async def get_report(parameters=Depends(ReportDatabase)):
    """Request an already calculated Report for an AOI defined by OQT.

    The response is a GeoJSON Feature with the Report results as properties.
    To request an Report for a custom AOI pease use the POST method.
    """
    return await _fetch_report(parameters)


@app.post("/report")
async def post_report(
    parameters: Union[ReportBpolys, ReportDatabase] = Body(
        ...,
        examples=REPORT_EXAMPLES,
    )
):
    """Request a Report for an AOI defined by OQT or a custom AOI.

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or FeatureCollection with
    the indicator results. The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    return await _fetch_report(parameters)


async def _fetch_report(
    parameters: Union[
        ReportBpolys,
        ReportDatabase,
    ],
):
    p = parameters.dict()
    dataset = p.get("dataset", None)
    fid_field = p.get("fid_field", None)
    if dataset is not None:
        dataset = dataset.value
    if fid_field is not None:
        fid_field = fid_field.value
    geojson_object = await oqt.create_report_as_geojson(
        p["name"].value,
        p.get("bpolys", None),
        dataset,
        p.get("feature_id", None),
        fid_field,
        size_restriction=True,
    )
    response = empty_api_response()
    if p["include_svg"] is False:
        remove_svg_from_properties(geojson_object)
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


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


def remove_svg_from_properties(
    geojson_object: Union[Feature, FeatureCollection]
) -> None:
    def _remove_svg_from_properties(properties: dict) -> None:
        for key in list(properties.keys()):
            if fnmatch.fnmatch(key, "*result.svg"):
                del properties[key]

    if isinstance(geojson_object, Feature):
        _remove_svg_from_properties(geojson_object["properties"])
    elif isinstance(geojson_object, FeatureCollection):
        for feature in geojson_object["features"]:
            _remove_svg_from_properties(feature["properties"])
