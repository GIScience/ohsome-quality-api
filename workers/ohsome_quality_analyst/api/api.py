import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


def empty_api_response() -> dict:
    return {
        "apiVersion": __version__,
        "attribution": {
            "text": "© OpenStreetMap contributors",
            "url": "https://ohsome.org/copyrights",
        },
    }


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

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
    """
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        # flake8 warning N806: variable 'fidField' in function should be lowercase
        # Ignore for Fast-API parameters which are definied as mixedCase
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

    Either the parameters `dataset` and `featureId` have to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
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
    if dataset is not None:
        dataset = dataset.value
    if fidField is not None:
        # flake8 warning N806: variable 'fidField' in function should be lowercase
        # Ignore for Fast-API parameters which are definied as mixedCase
        fidField = fidField.value  # noqa N806
    return await _fetch_report(name.value, bpolys, dataset, featureId, fidField)


@app.post("/report/{name}")
async def post_report(name: ReportEnum, parameters: ReportRequestModel):
    """Create a Report.

    Either the parameters `dataset` and `feature id` has to be provided
    or the parameter `bpolys` in form of a GeoJSON.

    Depending on the input, the output is a GeoJSON Feature or
    FeatureCollection with the indicator results.
    The Feature properties of the input GeoJSON will be preserved
    if they do not collide with the properties set by OQT.
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
async def get_available_regions(asGeoJSON: bool = False):
    """Get regions as list of names and identifiers or as GeoJSON.

    Args:
        asGeoJSON: If `True` regions will be returned as GeoJSON
    """
    response = empty_api_response()
    if asGeoJSON is True:
        regions = await db_client.get_regions_as_geojson()
        response.update(regions)
    else:
        regions = await db_client.get_regions()
        response["result"] = regions
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
