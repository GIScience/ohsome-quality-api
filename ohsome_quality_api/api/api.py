import json
import logging
import os
from typing import Any, Union

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse
from fastapi_i18n import i18n
from geojson import FeatureCollection
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from ohsome_quality_api import (
    __author__,
    __email__,
    __title__,
    __version__,
    oqt,
)
from ohsome_quality_api.api.request_context import set_request_context
from ohsome_quality_api.api.request_models import (
    AttributeCompletenessFilterRequest,
    AttributeCompletenessKeyRequest,
    IndicatorDataRequest,
    IndicatorRequest,
    LandCoverThematicAccuracyRequest,
)
from ohsome_quality_api.api.response_models import (
    AttributeMetadataResponse,
    IndicatorGeoJSONResponse,
    IndicatorJSONResponse,
    IndicatorMetadataCoverageResponse,
    IndicatorMetadataResponse,
    MetadataResponse,
    ProjectMetadataResponse,
    QualityDimensionMetadataResponse,
    TopicMetadataResponse,
)
from ohsome_quality_api.attributes.definitions import get_attributes, load_attributes
from ohsome_quality_api.config import configure_logging
from ohsome_quality_api.definitions import ATTRIBUTION_URL
from ohsome_quality_api.indicators.definitions import (
    IndicatorEnum,
    IndicatorEnumRequest,
    get_coverage,
    get_indicator,
    get_indicator_metadata,
)
from ohsome_quality_api.projects.definitions import (
    ProjectEnum,
    get_project,
    get_project_metadata,
)
from ohsome_quality_api.quality_dimensions.definitions import (
    QualityDimensionEnum,
    get_quality_dimension,
    get_quality_dimensions,
)
from ohsome_quality_api.topics.definitions import (
    TopicEnum,
    get_topic_preset,
    get_topic_presets,
)
from ohsome_quality_api.utils.exceptions import (
    OhsomeApiError,
    SizeRestrictionError,
    TopicDataSchemaError,
)
from ohsome_quality_api.utils.helper import (
    get_class_from_key,
    get_project_root,
    json_serialize,
)

MEDIA_TYPE_GEOJSON = "application/geo+json"
MEDIA_TYPE_JSON = "application/json"
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

TAGS_METADATA = [
    {"name": "indicator", "description": "Request an Indicator"},
    {"name": "metadata", "description": "Request Metadata"},
]

# TODO: to be replaced by config
DEFAULT_PROJECT = ProjectEnum.core

configure_logging()
logging.info("Logging enabled")
logging.debug("Debugging output enabled")

description = """
Data quality estimations for OpenStreetMap.

[Homepage](https://api.quality.ohsome.org) | [Dashboard](https://dashboard.ohsome.org/#backend=oqapi)
"""

if "FASTAPI_I18N_LOCALE_DIR" not in os.environ:
    os.environ["FASTAPI_I18N_LOCALE_DIR"] = os.path.join(
        get_project_root(), "ohsome_quality_api/locale"
    )

app = FastAPI(
    title=__title__,
    description=description,
    version=__version__,
    contact={
        "name": __author__,
        "email": __email__,
    },
    openapi_tags=TAGS_METADATA,
    docs_url=None,
    redoc_url=None,
    dependencies=[Depends(set_request_context), Depends(i18n)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(request: Request):
    root_path = request.scope.get("root_path")
    return get_swagger_ui_html(
        openapi_url=root_path + app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=root_path + "/static/swagger-ui-bundle.js",
        swagger_css_url=root_path + "/static/swagger-ui.css",
        swagger_favicon_url=root_path + "/static/favicon-32x32.png",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html(request: Request):
    root_path = request.scope.get("root_path")
    return get_redoc_html(
        openapi_url=root_path + app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url=root_path + "/static/redoc.standalone.js",
        redoc_favicon_url=root_path + "/static/favicon-32x32.png",
    )


class CustomJSONResponse(JSONResponse):
    def render(self, content):
        return json.dumps(content, default=json_serialize).encode()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request,
    exception: RequestValidationError,
):
    """Exception handler for validation exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "apiVersion": __version__,
                "type": exception.__class__.__name__,
                "detail": exception.errors(),
            },
        ),
    )


@app.exception_handler(TopicDataSchemaError)
@app.exception_handler(OhsomeApiError)
@app.exception_handler(SizeRestrictionError)
async def custom_exception_handler(
    _: Request, exception: TopicDataSchemaError | OhsomeApiError | SizeRestrictionError
):
    """Exception handler for custom exceptions."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "apiVersion": __version__,
            "type": exception.name,
            "detail": [
                {
                    "msg": exception.message,
                },
            ],
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exception: StarletteHTTPException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            "apiVersion": __version__,
            "type": exception.__class__.__name__,
            "detail": [
                {
                    "msg": exception.detail,
                },
            ],
        },
    )


def empty_api_response() -> dict:
    return {
        "apiVersion": __version__,
        "attribution": {
            "url": ATTRIBUTION_URL,
        },
    }


@app.post("/indicators/mapping-saturation/data", include_in_schema=False)
async def post_indicator_ms(parameters: IndicatorDataRequest) -> CustomJSONResponse:
    """Legacy support for computing the Mapping Saturation indicator for given data."""
    indicators = await oqt.create_indicator(
        key="mapping-saturation",
        bpolys=parameters.bpolys,
        topic=parameters.topic,
        include_figure=parameters.include_figure,
    )
    geojson_object = FeatureCollection(
        features=[i.as_feature(parameters.include_data) for i in indicators]
    )
    response = empty_api_response()
    response["attribution"]["text"] = get_class_from_key(
        class_type="indicator",
        key="mapping-saturation",
    ).attribution()
    response["result"] = [feature.properties for feature in geojson_object.features]
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_JSON)


@app.post(
    "/indicators/attribute-completeness",
    tags=["indicator"],
    response_model=Union[IndicatorJSONResponse, IndicatorGeoJSONResponse],
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorJSONResponse"}
                },
                "application/geo+json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorGeoJSONResponse"}
                },
            },
        },
    },
)
async def post_attribute_completeness(
    request: Request,
    parameters: AttributeCompletenessKeyRequest | AttributeCompletenessFilterRequest,
) -> Any:
    """Request the Attribute Completeness indicator for your area of interest."""
    return await _post_indicator(request, "attribute-completeness", parameters)


@app.post(
    "/indicators/land-cover-thematic-accuracy",
    tags=["indicator"],
    response_model=Union[IndicatorJSONResponse, IndicatorGeoJSONResponse],
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorJSONResponse"}
                },
                "application/geo+json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorGeoJSONResponse"}
                },
            },
        },
    },
)
async def post_land_cover_thematic_accuracy(
    request: Request, parameters: LandCoverThematicAccuracyRequest
) -> Any:
    """Request the Land Cover Thematic Accuracy indicator for your area of interest."""
    return await _post_indicator(request, "land-cover-thematic-accuracy", parameters)


@app.post(
    "/indicators/{key}",
    tags=["indicator"],
    response_model=Union[IndicatorJSONResponse, IndicatorGeoJSONResponse],
    responses={
        200: {
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorJSONResponse"}
                },
                "application/geo+json": {
                    "schema": {"$ref": "#/components/schemas/IndicatorGeoJSONResponse"}
                },
            },
        },
    },
)
async def post_indicator(
    request: Request, key: IndicatorEnumRequest, parameters: IndicatorRequest
) -> Any:
    """Request an indicator for your area of interest."""
    return await _post_indicator(request, key.value, parameters)


async def _post_indicator(
    request: Request,
    key: str,
    parameters: IndicatorRequest,
) -> Any:
    indicators = await oqt.create_indicator(key=key, **dict(parameters))

    if request.headers["accept"] == MEDIA_TYPE_JSON:
        return {
            "result": [i.as_dict(exclude_label=True) for i in indicators],
            "attribution": {
                "url": ATTRIBUTION_URL,
                "text": indicators[0].attribution(),
            },
        }
    elif request.headers["accept"] == MEDIA_TYPE_GEOJSON:
        return {
            "type": "FeatureCollection",
            "features": [i.as_feature(exclude_label=True) for i in indicators],
            "attribution": {
                "url": ATTRIBUTION_URL,
                "text": indicators[0].attribution(),
            },
        }
    else:
        detail = "Content-Type needs to be either {0} or {1}".format(
            MEDIA_TYPE_JSON,
            MEDIA_TYPE_GEOJSON,
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=detail,
        )


@app.get("/metadata", tags=["metadata"], response_model=MetadataResponse)
async def metadata(project: ProjectEnum = DEFAULT_PROJECT) -> Any:
    """All metadata."""
    if project == ProjectEnum.all:
        project = None
    return {
        "result": {
            "topics": get_topic_presets(project=project),
            "quality_dimensions": get_quality_dimensions(),
            "projects": get_project_metadata(),
            "indicators": get_indicator_metadata(project=project),
            "attributes": get_attributes(),
        }
    }


@app.get("/metadata/topics", tags=["metadata"], response_model=TopicMetadataResponse)
async def metadata_topic(project: ProjectEnum = DEFAULT_PROJECT) -> Any:
    """Get topics."""
    if project == ProjectEnum.all:
        project = None
    return {"result": get_topic_presets(project=project)}


@app.get(
    "/metadata/topics/{key}",
    tags=["metadata"],
    response_model=TopicMetadataResponse,
)
async def metadata_topic_by_key(key: TopicEnum) -> Any:
    """Get topic by key."""
    return {"result": {key.value: get_topic_preset(key.value)}}


@app.get(
    "/metadata/attributes",
    tags=["metadata"],
    response_model=AttributeMetadataResponse,
)
async def metadata_attribute() -> Any:
    """Get all attributes."""
    return {"result": load_attributes()}


@app.get(
    "/metadata/quality-dimensions",
    tags=["metadata"],
)
async def metadata_quality_dimensions() -> QualityDimensionMetadataResponse:
    """Get quality dimensions."""
    return QualityDimensionMetadataResponse(result=get_quality_dimensions())


@app.get("/metadata/quality-dimensions/{key}", tags=["metadata"])
async def metadata_quality_dimension_by_key(
    key: QualityDimensionEnum,
) -> QualityDimensionMetadataResponse:
    """Get quality dimension by key."""
    return QualityDimensionMetadataResponse(
        result={key.value: get_quality_dimension(key.value)}
    )


@app.get(
    "/metadata/projects",
    tags=["metadata"],
)
async def metadata_projects() -> ProjectMetadataResponse:
    """Get projects."""
    return ProjectMetadataResponse(result=get_project_metadata())


@app.get(
    "/metadata/projects/{key}",
    tags=["metadata"],
)
async def metadata_project_by_key(
    key: ProjectEnum,
) -> ProjectMetadataResponse:
    """Get project by key."""
    return ProjectMetadataResponse(result={key.value: get_project(key.value)})


@app.get(
    "/metadata/indicators",
    tags=["metadata"],
    response_model=IndicatorMetadataResponse,
)
async def metadata_indicators(project: ProjectEnum = DEFAULT_PROJECT) -> Any:
    """Get metadata of all indicators."""
    if project == ProjectEnum.all:
        project = None
    return {"result": get_indicator_metadata(project=project)}


@app.get(
    "/metadata/indicators/{key}",
    tags=["metadata"],
    response_model=IndicatorMetadataResponse,
)
async def metadata_indicators_by_key(key: IndicatorEnum) -> Any:
    """Get metadata of an indicator by key."""
    metadata = get_indicator(key.value)
    return {"result": {key.value: metadata}}


@app.get(
    "/metadata/indicators/{key}/coverage",
    tags=["metadata"],
    response_model=IndicatorMetadataCoverageResponse,
)
async def metadata_indicators_coverage(
    key: IndicatorEnum,
    inverse: bool = False,
) -> Any:
    """Get coverage geometry of an indicator by key."""
    return await get_coverage(key.value, inverse)
