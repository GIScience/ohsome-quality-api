import json
import logging
import os
from typing import Annotated

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
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

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
    IndicatorDataRequest,
    IndicatorEnum,
    IndicatorRequest,
    ReportEnum,
    ReportRequest,
    TopicEnum,
)
from ohsome_quality_analyst.api.response_models import (
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
    get_indicator_definitions,
    get_metadata,
    get_report_definitions,
    get_topic_definition,
    get_topic_definitions,
)
from ohsome_quality_analyst.projects.definitions import (
    ProjectEnum,
    get_project,
    get_projects,
)
from ohsome_quality_analyst.quality_dimensions.definitions import (
    QualityDimensionEnum,
    get_quality_dimension,
    get_quality_dimensions,
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
    geojson_object = await oqt.create_indicator_as_geojson(
        parameters,
        key="mapping-saturation",
    )
    response = empty_api_response()
    response["attribution"]["text"] = get_class_from_key(
        class_type="indicator",
        key="mapping-saturation",
    ).attribution()
    # TODO: if accept=JSON no GeoJSON should be created in the first place.
    #   factor out logic and decision to base/indicator.py and oqt.py
    #   base/indicator.py should have `as_dict` alongside `as_feature`
    response["results"] = [feature.properties for feature in geojson_object.features]
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_JSON)


@app.post(
    "/indicators/{key}",
    tags=["indicator"],
    responses={
        200: {
            "content": {MEDIA_TYPE_GEOJSON: {}},
            "description": "Return JSON or GeoJSON.",
        }
    },
)
async def post_indicator(
    request: Request,
    key: Annotated[
        IndicatorEnum,
        Path(
            title="Indicator Key",
            example="mapping-saturation",
        ),
    ],
    parameters: IndicatorRequest,
) -> CustomJSONResponse:
    """Request an Indicator for an AOI defined by OQT or a custom AOI."""
    if isinstance(parameters, IndicatorRequest):
        validate_indicator_topic_combination(key.value, parameters.topic_key.value)
    geojson_object = await oqt.create_indicator_as_geojson(parameters, key=key.value)
    response = empty_api_response()
    response["attribution"]["text"] = get_class_from_key(
        class_type="indicator",
        key=key.value,
    ).attribution()
    # TODO: if accept=JSON no GeoJSON should be created in the first place.
    #   factor out logic and decision to base/indicator.py and oqt.py
    #   base/indicator.py should have `as_dict` alongside `as_feature`
    if request.headers["accept"] == MEDIA_TYPE_JSON:
        response["results"] = [
            feature.properties for feature in geojson_object.features
        ]
        return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_JSON)
    elif request.headers["accept"] == MEDIA_TYPE_GEOJSON:
        response.update(geojson_object)
        return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)
    else:
        detail = "Content-Type needs to be either {0} or {1}".format(
            MEDIA_TYPE_JSON, MEDIA_TYPE_GEOJSON
        )
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail=detail
        )


@app.post("/reports/{key}", tags=["report"])
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
    """Request a Report for an AOI defined by OQT or a custom AOI."""
    geojson_object = await oqt.create_report_as_geojson(parameters, key=key.value)
    response = empty_api_response()
    response["attribution"]["text"] = get_class_from_key(
        class_type="report",
        key=key.value,
    ).attribution()
    response.update(geojson_object)
    return CustomJSONResponse(content=response, media_type=MEDIA_TYPE_GEOJSON)


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
    if project == ProjectEnum.all:
        project = None
    result = {
        "topics": get_topic_definitions(project=project),
        "quality_dimensions": get_quality_dimensions(),
        "projects": get_projects(),
        "indicators": get_indicator_definitions(project=project),
        "reports": get_report_definitions(project=project),
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
    if project == ProjectEnum.all:
        project = None
    return TopicMetadataResponse(result=get_topic_definitions(project=project))


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
async def metadata_quality_dimensions() -> QualityDimensionMetadataResponse:
    """Get quality dimensions."""
    return QualityDimensionMetadataResponse(result=get_quality_dimensions())


@app.get(
    "/metadata/quality-dimensions/{key}",
    tags=["metadata"],
)
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
    return ProjectMetadataResponse(result=get_projects())


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
    if project == ProjectEnum.all:
        project = None
    return IndicatorMetadataResponse(result=get_indicator_definitions(project=project))


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
    if project == ProjectEnum.all:
        project = None
    return ReportMetadataResponse(result=get_report_definitions(project=project))


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
