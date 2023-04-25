import fnmatch
import json
import logging

from fastapi import Body, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from geojson import Feature, FeatureCollection
from pydantic import BaseModel, ValidationError

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
    IndicatorEnum,
    ProjectEnum,
    ReportBpolys,
    ReportDatabase,
    ReportEnum,
    TopicEnum,
)
from ohsome_quality_analyst.api.response_models import (
    IndicatorMetadataResponse,
    MetadataResponse,
    ReportMetadataResponse,
    TopicMetadataResponse,
)
from ohsome_quality_analyst.config import configure_logging
from ohsome_quality_analyst.definitions import (
    ATTRIBUTION_URL,
    get_attribution,
    get_dataset_names,
    get_fid_fields,
    get_indicator_definitions,
    get_indicator_names,
    get_metadata,
    get_report_definitions,
    get_report_names,
    get_topic_definition,
    get_topic_definitions,
)
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.exceptions import (
    HexCellsNotFoundError,
    OhsomeApiError,
    RasterDatasetNotFoundError,
    RasterDatasetUndefinedError,
    SizeRestrictionError,
    TopicDataSchemaError,
)
from ohsome_quality_analyst.utils.helper import (
    hyphen_to_camel,
    json_serialize,
    name_to_class,
    snake_to_hyphen,
)

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
    {
        "name": "metadata",
        "description": "Request Metadata",
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

# TODO: to be replaced by config
DEFAULT_PROJECT = ProjectEnum.core

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
    request: Request, exception: RequestValidationError | ValidationError
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
@app.exception_handler(TopicDataSchemaError)
@app.exception_handler(OhsomeApiError)
@app.exception_handler(RasterDatasetNotFoundError)
@app.exception_handler(RasterDatasetUndefinedError)
@app.exception_handler(SizeRestrictionError)
async def oqt_exception_handler(
    request: Request,
    exception: (
        HexCellsNotFoundError
        | TopicDataSchemaError
        | OhsomeApiError
        | RasterDatasetNotFoundError
        | RasterDatasetUndefinedError
        | SizeRestrictionError
    ),
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


# TODO (Experimental): Belongs to temporary endpoint defined below
class MappingSaturationModel(BaseModel):
    bpolys: Feature | FeatureCollection
    topic_key: str

    class Config:
        alias_generator = snake_to_hyphen


# TODO (Experimental): Make this endpoint general and remove `/indicator` endpoint below
@app.post("/indicators/mapping-saturation", tags=["indicator"], include_in_schema=False)
async def post_indicator_mapping_saturation(
    parameters: MappingSaturationModel,
) -> CustomJSONResponse:
    """Request an Indicator for an AOI."""
    parameters = IndicatorBpolys(
        name="mapping-saturation", topic=parameters.topic_key, bpolys=parameters.bpolys
    )
    return await post_indicator(parameters)


@app.post("/indicator", tags=["indicator"])
async def post_indicator(
    parameters: IndicatorBpolys
    | IndicatorDatabase
    | IndicatorData = Body(
        ...,
        examples=INDICATOR_EXAMPLES,
    ),
) -> CustomJSONResponse:
    """Request an Indicator for an AOI defined by OQT or a custom AOI."""
    geojson_object = await oqt.create_indicator_as_geojson(
        parameters,
        size_restriction=True,
    )
    if parameters.include_svg is False:
        remove_result_item_from_properties(
            geojson_object,
            "svg",
            parameters.flatten,
        )
    if parameters.include_html is False:
        remove_result_item_from_properties(
            geojson_object,
            "html",
            parameters.flatten,
        )
    response = empty_api_response()
    response["attribution"]["text"] = name_to_class(
        class_type="indicator",
        name=parameters.name.value,
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.post("/report", tags=["report"])
async def post_report(
    parameters: ReportBpolys
    | ReportDatabase = Body(
        ...,
        examples=REPORT_EXAMPLES,
    )
) -> CustomJSONResponse:
    """Request a Report for an AOI defined by OQT or a custom AOI."""
    geojson_object = await oqt.create_report_as_geojson(
        parameters,
        size_restriction=True,
    )
    if parameters.include_html is False:
        remove_result_item_from_properties(
            geojson_object,
            "html",
            parameters.flatten,
        )
    if parameters.include_svg is False:
        remove_result_item_from_properties(
            geojson_object,
            "svg",
            parameters.flatten,
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


@app.get(
    "/metadata",
    tags=["metadata"],
    response_model_exclude={
        "result": {
            "topics": {k.value: {"key": True} for k in TopicEnum},
            "indicators": {
                k.value: {"label_description": True, "result_description": True}
                for k in IndicatorEnum
            },
            "reports": {k.value: {"label_description": True} for k in ReportEnum},
        }
    },
)
async def metadata(project: ProjectEnum = DEFAULT_PROJECT) -> MetadataResponse:
    """Get topics."""
    result = {
        "topics": get_topic_definitions(project=project.value),
        "indicators": get_indicator_definitions(project=project.value),
        "reports": get_report_definitions(project=project.value),
    }
    return MetadataResponse(result=result)


@app.get(
    "/metadata/topics",
    tags=["metadata"],
    response_model_exclude={
        "result": {k.value: {"key": True} for k in TopicEnum},
    },
)
async def metadata_topic(
    project: ProjectEnum = DEFAULT_PROJECT,
) -> TopicMetadataResponse:
    """Get topics."""
    return TopicMetadataResponse(result=get_topic_definitions(project=project.value))


@app.get(
    "/metadata/topics/{key}",
    tags=["metadata"],
    response_model_exclude={"result": {k.value: {"key": True} for k in TopicEnum}},
)
async def metadata_topic_by_key(key: TopicEnum) -> TopicMetadataResponse:
    """Get topic by key."""
    return TopicMetadataResponse(result={key.value: get_topic_definition(key.value)})


@app.get(
    "/metadata/indicators",
    tags=["metadata"],
    response_model_exclude={
        "result": {
            k.value: {"label_description": True, "result_description": True}
            for k in IndicatorEnum
        },
    },
)
async def metadata_indicators(
    project: ProjectEnum = DEFAULT_PROJECT,
) -> IndicatorMetadataResponse:
    """Get metadata of all indicators."""
    return IndicatorMetadataResponse(
        result=get_indicator_definitions(project=project.value)
    )


@app.get(
    "/metadata/indicators/{key}",
    tags=["metadata"],
    response_model_exclude={
        "result": {
            k.value: {"label_description": True, "result_description": True}
            for k in IndicatorEnum
        }
    },
)
async def metadata_indicators_by_key(key: IndicatorEnum) -> IndicatorMetadataResponse:
    """Get metadata of an indicator by key."""
    return IndicatorMetadataResponse(
        result={key.value: get_metadata("indicators", hyphen_to_camel(key.value))}
    )


@app.get(
    "/metadata/reports",
    tags=["metadata"],
    response_model_exclude={
        "result": {k.value: {"label_description": True} for k in ReportEnum}
    },
)
async def metadata_reports(
    project: ProjectEnum = DEFAULT_PROJECT,
) -> ReportMetadataResponse:
    """Get metadata of all indicators."""
    return ReportMetadataResponse(result=get_report_definitions(project=project.value))


@app.get(
    "/metadata/reports/{key}",
    tags=["metadata"],
    response_model_exclude={
        "result": {k.value: {"label_description": True} for k in ReportEnum}
    },
)
async def metadata_reports_by_key(key: ReportEnum) -> ReportMetadataResponse:
    """Get metadata of an indicator by key."""
    return ReportMetadataResponse(
        result={key.value: get_metadata("reports", hyphen_to_camel(key.value))}
    )


def remove_result_item_from_properties(
    geojson_object: Feature | FeatureCollection, key: str, flatten: bool
) -> None:
    """Remove item from the properties of a GeoJSON Feature or FeatureCollection.

    If properties are flattened pattern matching (See 'fnmatch.fnmatch') is used to
    delete the item with given key from the properties, else item with given key will
    be removed.
    """

    def _remove_item_from_properties_pattern(properties: dict, pattern: str) -> None:
        for key in list(properties.keys()):
            if fnmatch.fnmatch(key, pattern):
                del properties[key]

    def _remove_item_from_properties_key(properties: dict, key: str) -> None:
        if "result" in properties.keys():
            properties["result"].pop(key, None)
        if "report" in properties.keys():
            properties["report"]["result"].pop(key, None)
        if "indicators" in properties.keys():
            for indicator in properties["indicators"]:
                indicator["result"].pop(key, None)

    if isinstance(geojson_object, Feature):
        if flatten:
            pattern = "*result." + key
            _remove_item_from_properties_pattern(geojson_object["properties"], pattern)
        else:
            _remove_item_from_properties_key(geojson_object["properties"], key)
    elif isinstance(geojson_object, FeatureCollection):
        for feature in geojson_object["features"]:
            if flatten:
                pattern = "*result." + key
                _remove_item_from_properties_pattern(feature["properties"], pattern)
            else:
                _remove_item_from_properties_key(feature["properties"], key)
