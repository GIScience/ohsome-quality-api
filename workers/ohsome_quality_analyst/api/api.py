import fnmatch
import json
import logging
from typing import Annotated

from fastapi import Body, FastAPI, Path, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from geojson import Feature, FeatureCollection
from pydantic import BaseModel

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
    QualityDimensionEnum,
    ReportBpolys,
    ReportDatabase,
    ReportEnum,
    TopicEnum,
)
from ohsome_quality_analyst.api.response_models import (
    IndicatorMetadataResponse,
    MetadataResponse,
    QualityDimensionMetadataResponse,
    ReportMetadataResponse,
    TopicMetadataResponse,
)
from ohsome_quality_analyst.config import configure_logging
from ohsome_quality_analyst.definitions import (
    ATTRIBUTION_URL,
    get_attribution,
    get_indicator_definitions,
    get_metadata,
    get_quality_dimension,
    get_quality_dimensions,
    get_report_definitions,
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
    ValidationError,
)
from ohsome_quality_analyst.utils.helper import (
    get_class_from_key,
    hyphen_to_camel,
    json_serialize,
    snake_to_hyphen,
)
from ohsome_quality_analyst.utils.validators import validate_indicator_topic_combination

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


@app.exception_handler(RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(
    request: Request,
    exception: RequestValidationError | ValidationError,
):
    """Exception handler for validation exceptions."""
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
    """Exception handler for OQT exceptions."""
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


@app.post("/indicators/{key}", tags=["indicator"])
async def post_indicator(
    key: Annotated[
        IndicatorEnum,
        Path(
            title="Indicator Key",
            example="mapping-saturation",
        ),
    ],
    parameters: IndicatorBpolys
    | IndicatorDatabase
    | IndicatorData = Body(
        ...,
        examples=INDICATOR_EXAMPLES,
    ),
) -> CustomJSONResponse:
    """Request an Indicator for an AOI defined by OQT or a custom AOI."""
    if isinstance(parameters, (IndicatorBpolys, IndicatorDatabase)):
        validate_indicator_topic_combination(key.value, parameters.topic_key.value)
    geojson_object = await oqt.create_indicator_as_geojson(
        parameters,
        key=key.value,
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
    response["attribution"]["text"] = get_class_from_key(
        class_type="indicator",
        key=key.value,
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.post("/reports/{key}", tags=["report"])
async def post_report(
    key: Annotated[
        ReportEnum,
        Path(
            title="Report Key",
            example="building-report",
        ),
    ],
    parameters: ReportBpolys
    | ReportDatabase = Body(
        ...,
        examples=REPORT_EXAMPLES,
    ),
) -> CustomJSONResponse:
    """Request a Report for an AOI defined by OQT or a custom AOI."""
    geojson_object = await oqt.create_report_as_geojson(
        parameters,
        key=key.value,
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
    response["attribution"]["text"] = get_class_from_key(
        class_type="report",
        key=key.value,
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
        "quality-dimensions": get_quality_dimensions(),
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
    "/metadata/quality-dimensions",
    tags=["metadata"],
)
async def metadata_quality_dimension() -> QualityDimensionMetadataResponse:
    """Get topics."""
    return QualityDimensionMetadataResponse(result=get_quality_dimensions())


@app.get(
    "/metadata/quality-dimensions/{key}",
    tags=["metadata"],
)
async def metadata_quality_dimension_by_key(
    key: QualityDimensionEnum,
) -> QualityDimensionMetadataResponse:
    """Get topic by key."""
    return QualityDimensionMetadataResponse(
        result={key.value: get_quality_dimension(key.value)}
    )


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
