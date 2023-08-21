import json
import logging
import os
from typing import Annotated, Any, Union

from fastapi import FastAPI, HTTPException, Path, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.responses import JSONResponse
from geojson import FeatureCollection
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from ohsome_quality_analyst import (
    __author__,
    __email__,
    __title__,
    __version__,
    oqt,
)
from ohsome_quality_analyst.api.request_models import (
    IndicatorDataRequest,
    IndicatorRequest,
    ReportRequest,
)
from ohsome_quality_analyst.api.response_models import (
    IndicatorGeoJSONResponse,
    IndicatorJSONResponse,
    IndicatorMetadataResponse,
    MetadataResponse,
    ProjectMetadataResponse,
    QualityDimensionMetadataResponse,
    ReportMetadataResponse,
    TopicMetadataResponse,
)
from ohsome_quality_analyst.config import configure_logging
from ohsome_quality_analyst.definitions import (
    ATTRIBUTION_URL,
    get_metadata,
)
from ohsome_quality_analyst.indicators.definitions import (
    IndicatorEnum,
    get_indicator_metadata,
)
from ohsome_quality_analyst.projects.definitions import (
    ProjectEnum,
    get_project,
    get_project_metadata,
)
from ohsome_quality_analyst.quality_dimensions.definitions import (
    QualityDimensionEnum,
    get_quality_dimension,
    get_quality_dimensions,
)
from ohsome_quality_analyst.reports.definitions import (
    ReportEnum,
    get_report_metadata,
)
from ohsome_quality_analyst.topics.definitions import (
    TopicEnum,
    get_topic_preset,
    get_topic_presets,
)
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
)
from ohsome_quality_analyst.utils.validators import validate_indicator_topic_combination

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

[Homepage](https://oqt.ohsome@heigit.org) | [Dashboard](https://dashboard.ohsome.org/#backend=oqtApi)
"""

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


@app.exception_handler(HexCellsNotFoundError)
@app.exception_handler(TopicDataSchemaError)
@app.exception_handler(OhsomeApiError)
@app.exception_handler(RasterDatasetNotFoundError)
@app.exception_handler(RasterDatasetUndefinedError)
@app.exception_handler(SizeRestrictionError)
@app.exception_handler(ValidationError)
async def oqt_exception_handler(
    _: Request,
    exception: HexCellsNotFoundError
    | TopicDataSchemaError
    | OhsomeApiError
    | RasterDatasetNotFoundError
    | RasterDatasetUndefinedError
    | SizeRestrictionError
    | ValidationError,
):
    """Exception handler for OQT exceptions."""
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
    # TODO: if accept=JSON no GeoJSON should be created in the first place.
    response["result"] = [feature.properties for feature in geojson_object.features]
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_JSON)


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
    request: Request,
    key: IndicatorEnum,
    parameters: IndicatorRequest,
) -> Any:
    """Request an indicator for your area of interest."""
    validate_indicator_topic_combination(key.value, parameters.topic_key.value)
    indicators = await oqt.create_indicator(
        key=key.value,
        bpolys=parameters.bpolys,
        topic=get_topic_preset(parameters.topic_key.value),
        include_figure=parameters.include_figure,
    )

    if request.headers["accept"] == MEDIA_TYPE_JSON:
        return {
            "result": [
                i.as_dict(parameters.include_data, exclude_label=True)
                for i in indicators
            ],
            "attribution": {
                "url": ATTRIBUTION_URL,
                "text": indicators[0].attribution(),
            },
        }
    elif request.headers["accept"] == MEDIA_TYPE_GEOJSON:
        return {
            "type": "FeatureCollection",
            "features": [
                i.as_feature(parameters.include_data, exclude_label=True)
                for i in indicators
            ],
            "attribution": {
                "url": ATTRIBUTION_URL,
                "text": indicators[0].attribution(),
            },
        }
    else:
        detail = "Content-Type needs to be either {0} or {1}".format(
            MEDIA_TYPE_JSON, MEDIA_TYPE_GEOJSON
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail
        )


@app.post("/reports/{key}", include_in_schema=False)
async def post_report(
    key: Annotated[
        ReportEnum,
        Path(
            title="Report Key",
            example="building-report",
        ),
    ],
    parameters: ReportRequest,
) -> CustomJSONResponse:
    geojson_object = await oqt.create_report(parameters, key=key.value)
    response = empty_api_response()
    response["attribution"]["text"] = get_class_from_key(
        class_type="report",
        key=key.value,
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


@app.get("/metadata", tags=["metadata"], response_model=MetadataResponse)
async def metadata(project: ProjectEnum = DEFAULT_PROJECT) -> Any:
    """Get topics."""
    if project == ProjectEnum.all:
        project = None
    return {
        "result": {
            "topics": get_topic_presets(project=project),
            "quality_dimensions": get_quality_dimensions(),
            "projects": get_project_metadata(),
            "indicators": get_indicator_metadata(project=project),
            # "reports": get_report_metadata(project=project),
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
    metadata = get_metadata("indicators", hyphen_to_camel(key.value))
    return {"result": {key.value: metadata}}


@app.get(
    "/metadata/reports",
    tags=["metadata"],
    response_model_exclude={
        "result": {k.value: {"label_description": True} for k in ReportEnum}
    },
    include_in_schema=False,
)
async def metadata_reports(
    project: ProjectEnum = DEFAULT_PROJECT,
) -> ReportMetadataResponse:
    """Get metadata of all indicators."""
    if project == ProjectEnum.all:
        project = None
    return ReportMetadataResponse(result=get_report_metadata(project=project))


@app.get(
    "/metadata/reports/{key}",
    tags=["metadata"],
    response_model_exclude={
        "result": {k.value: {"label_description": True} for k in ReportEnum}
    },
    include_in_schema=False,
)
async def metadata_reports_by_key(key: ReportEnum) -> ReportMetadataResponse:
    """Get metadata of an indicator by key."""
    return ReportMetadataResponse(
        result={key.value: get_metadata("reports", hyphen_to_camel(key.value))}
    )
