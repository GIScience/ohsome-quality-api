import json
import logging
from typing import Union

from fastapi import Body, Depends, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
    IndicatorData,
    IndicatorDatabase,
    ReportBpolys,
    ReportDatabase,
)
from ohsome_quality_analyst.config import configure_logging
from ohsome_quality_analyst.definitions import (
    ATTRIBUTION_URL,
    INDICATOR_LAYER,
    get_attribution,
    get_dataset_names,
    get_fid_fields,
    get_indicator_names,
    get_layer_keys,
    get_report_names,
)
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.exceptions import (
    HexCellsNotFoundError,
    LayerDataSchemaError,
    OhsomeApiError,
    RasterDatasetNotFoundError,
    RasterDatasetUndefinedError,
    SizeRestrictionError,
)
from ohsome_quality_analyst.utils.helper import json_serialize, name_to_class

MEDIA_TYPE_GEOJSON = "application/geo+json"

TAGS_METADATA = [
    {
        "name": "indicator",
        "description": "Request an Indicator",
        "externalDocs": {
            "description": "External docs",
            "url": (
                "https://github.com/GIScience/ohsome-quality-analyst/blob/"
                + __version__
                + "/docs/api.md"
            ),
        },
    },
    {
        "name": "report",
        "description": "Request a Report",
        "externalDocs": {
            "description": "External docs",
            "url": (
                "https://github.com/GIScience/ohsome-quality-analyst/blob/"
                + __version__
                + "/docs/api.md"
            ),
        },
    },
]

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
    openapi_tags=TAGS_METADATA,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CustomJSONResponse(JSONResponse):
    def render(self, content):
        return json.dumps(content, default=json_serialize).encode()


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


@app.exception_handler(HexCellsNotFoundError)
@app.exception_handler(LayerDataSchemaError)
@app.exception_handler(OhsomeApiError)
@app.exception_handler(RasterDatasetNotFoundError)
@app.exception_handler(RasterDatasetUndefinedError)
@app.exception_handler(SizeRestrictionError)
async def oqt_exception_handler(
    request: Request,
    exception: Union[
        HexCellsNotFoundError,
        LayerDataSchemaError,
        OhsomeApiError,
        RasterDatasetNotFoundError,
        RasterDatasetUndefinedError,
        SizeRestrictionError,
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
            "url": ATTRIBUTION_URL,
        },
    }


@app.get("/indicator", tags=["indicator"])
async def get_indicator(parameters=Depends(IndicatorDatabase)):
    """Request an Indicator for an AOI defined by OQT.

    To request an Indicator for a custom AOI please use the POST method.
    """
    return await _fetch_indicator(parameters)


@app.post("/indicator", tags=["indicator"])
async def post_indicator(
    parameters: Union[IndicatorBpolys, IndicatorDatabase, IndicatorData] = Body(
        ...,
        examples=INDICATOR_EXAMPLES,
    ),
):
    """Request an Indicator for an AOI defined by OQT or a custom AOI."""
    return await _fetch_indicator(parameters)


async def _fetch_indicator(parameters) -> CustomJSONResponse:
    geojson_object = await oqt.create_indicator_as_geojson(
        parameters,
        size_restriction=True,
    )
    response = empty_api_response()
    response["attribution"]["text"] = name_to_class(
        class_type="indicator",
        name=parameters.name.value,
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.get("/report", tags=["report"])
async def get_report(parameters=Depends(ReportDatabase)):
    """Request an already calculated Report for an AOI defined by OQT.

    To request an Report for a custom AOI please use the POST method.
    """
    return await _fetch_report(parameters)


@app.post("/report", tags=["report"])
async def post_report(
    parameters: Union[ReportBpolys, ReportDatabase] = Body(
        ...,
        examples=REPORT_EXAMPLES,
    )
):
    """Request a Report for an AOI defined by OQT or a custom AOI."""
    return await _fetch_report(parameters)


async def _fetch_report(parameters: Union[ReportBpolys, ReportDatabase]):
    geojson_object = await oqt.create_report_as_geojson(
        parameters,
        size_restriction=True,
    )
    response = empty_api_response()
    response["attribution"]["text"] = name_to_class(
        class_type="report", name=parameters.name.value
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.get("/regions")
async def get_available_regions(asGeoJSON: bool = False):
    """Get regions as list of names and identifiers or as a GeoJSON."""
    response = empty_api_response()
    if asGeoJSON is True:
        regions = await db_client.get_regions_as_geojson()
        response.update(regions)
        response["attribution"]["text"] = get_attribution(["OSM"])
        return JSONResponse(
            content=jsonable_encoder(response), media_type=MEDIA_TYPE_GEOJSON
        )
    else:
        response["result"] = await db_client.get_regions()
        return response


@app.get("/indicator-layer-combinations")
async def get_indicator_layer_combinations():
    """Get names of available indicator-layer combinations."""
    response = empty_api_response()
    response["result"] = INDICATOR_LAYER
    return response


@app.get("/indicators")
async def indicator_names():
    """Get names of available indicators."""
    response = empty_api_response()
    response["result"] = get_indicator_names()
    return response


@app.get("/datasets")
async def dataset_names():
    """Get names of available datasets."""
    response = empty_api_response()
    response["result"] = get_dataset_names()
    return response


@app.get("/layers")
async def layer_names():
    """Get names of available layers."""
    response = empty_api_response()
    response["result"] = get_layer_keys()
    return response


@app.get("/reports")
async def report_names():
    """Get names of available reports."""
    response = empty_api_response()
    response["result"] = get_report_names()
    return response


@app.get("/fid-fields")
async def list_fid_fields():
    """List available fid fields for each dataset."""
    response = empty_api_response()
    response["result"] = get_fid_fields()
    return response
