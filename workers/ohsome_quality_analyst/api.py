import logging
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ohsome_quality_analyst import __version__ as oqt_version
from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.definitions import (
    DATASETS,
    configure_logging,
    load_layer_definitions,
    load_metadata,
)

configure_logging()
logging.info("Logging enabled")
logging.debug("Debugging output enabled")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IndicatorParameters(BaseModel):
    bpolys: Optional[str] = None
    dataset: Optional[str] = None
    featureId: Optional[str] = None
    layerName: Optional[str] = None
    fidField: Optional[str] = None


class ReportParameters(BaseModel):
    bpolys: Optional[str] = None
    dataset: Optional[str] = None
    featureId: Optional[str] = None
    fidField: Optional[str] = None


def empty_api_response(request_url: str) -> dict:
    return {
        "apiVersion": oqt_version,
        "attribution": {
            "text": "© OpenStreetMap contributors",
            "url": "https://ohsome.org/copyrights",
        },
        "requestUrl": request_url,
    }


@app.get("/indicator/{name}")
async def get_indicator(
    name: str,
    request: Request,
    layerName: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    featureId: Optional[str] = None,
    fidField: Optional[str] = None,
):
    return await _fetch_indicator(
        name, layerName, request.url._url, bpolys, dataset, featureId, fidField
    )


@app.post("/indicator/{name}")
async def post_indicator(name: str, request: Request, item: IndicatorParameters):
    # TODO: Check if default parameter None is necessary (item has default values)
    layer_name = item.dict().get("layerName", None)
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("featureId", None)
    fid_field = item.dict().get("fidField", None)
    return await _fetch_indicator(
        name, layer_name, request.url._url, bpolys, dataset, feature_id, fid_field
    )


async def _fetch_indicator(
    name: str,
    layer_name: str,
    request_url: str,
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
    response = empty_api_response(request_url)
    response.update(geojson_object)
    return response


@app.get("/report/{name}")
async def get_report(
    name: str,
    request: Request,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    featureId: Optional[str] = None,
    fidField: Optional[str] = None,
):
    return await _fetch_report(
        name, request.url._url, bpolys, dataset, featureId, fidField
    )


@app.post("/report/{name}")
async def post_report(name: str, request: Request, item: ReportParameters):
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("featureId", None)
    fid_field = item.dict().get("fidField", None)
    return await _fetch_report(
        name, request.url._url, bpolys, dataset, feature_id, fid_field
    )


async def _fetch_report(
    name: str,
    request_url: str,
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
    response = empty_api_response(request_url)
    response.update(geojson_object)
    return response


@app.get("/regions")
async def get_available_regions(
    request: Request,
):
    """List names of available regions."""

    response = empty_api_response(request.url._url)
    result = await db_client.get_available_regions()
    response.update(result)
    return response


@app.get("/indicatorNames")
async def list_indicators(
    request: Request,
):
    """List names of available indicators."""
    response = empty_api_response(request.url._url)
    response["result"] = list(load_metadata("indicators").keys())
    return response


@app.get("/datasetNames")
async def list_datasets(
    request: Request,
):
    """List names of available datasets."""
    response = empty_api_response(request.url._url)
    response["result"] = list((DATASETS.keys()))
    return response


@app.get("/layerNames")
async def list_layers(
    request: Request,
):
    """List names of available layers."""
    response = empty_api_response(request.url._url)
    response["result"] = list(load_layer_definitions().keys())
    return response


@app.get("/reportNames")
async def list_reports(
    request: Request,
):
    """List names of available reports."""
    response = empty_api_response(request.url._url)
    response["result"] = list(load_metadata("reports").keys())
    return response


@app.get("/FidFields")
async def list_fid_fields(
    request: Request,
):
    """List available fid fields for each dataset."""
    response = empty_api_response(request.url._url)
    fid_fields = []
    for _, dataset in DATASETS.items():
        fid_fields.append(dataset["default"])
        if "other" in dataset.keys():
            fid_fields += list(dataset["other"])
    response["result"] = fid_fields
    return response
