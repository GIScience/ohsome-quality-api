import json
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ohsome_quality_tool import oqt
from ohsome_quality_tool.geodatabase import client as db_client

RESPONSE_TEMPLATE = {
    "attribution": {
        "url": "https://ohsome.org/copyrights",
        "text": "© OpenStreetMap contributors",
    },
    "apiVersion": "0.1",
    "metadata": "",
    "result": "",
}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Parameters(BaseModel):
    bpolys: Optional[str] = None
    dataset: Optional[str] = None
    feature_id: Optional[str] = None


@app.get("/indicator/{name}")
async def get_indicator(
    name: str,
    request: Request,
    layer_name: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
):
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and feature_id is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    indicator = oqt.create_indicator(name, layer_name, bpolys, dataset, feature_id)
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(indicator.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = vars(indicator.result)
    return response


@app.post("/indicator/{name}/{layer_name}")
async def post_indicator(
    name: str, request: Request, layer_name: str, item: Parameters
):
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("feature_id", None)
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and feature_id is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    indicator = oqt.create_indicator(name, layer_name, bpolys, dataset, feature_id)
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(indicator.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = vars(indicator.result)
    return response


@app.get("/report/{name}")
async def get_report(
    name: str,
    request: Request,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    feature_id: Optional[str] = None,
):
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and feature_id is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    report = oqt.create_report(
        name, bpolys=bpolys, dataset=dataset, feature_id=feature_id
    )
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(report.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = vars(report.result)
    response["indicators"] = [vars(indicator) for indicator in report.indicators]
    return response


@app.post("/report/{name}")
async def post_report(name: str, request: Request, item: Parameters):
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("feature_id", None)
    if bpolys:
        bpolys = json.loads(bpolys)
    report = oqt.create_report(
        name, bpolys=bpolys, dataset=dataset, feature_id=feature_id
    )
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(report.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = vars(report.result)
    response["indicators"] = [vars(indicator) for indicator in report.indicators]
    return response


@app.get("/geometries/{dataset}")
async def get_bpolys_from_db(dataset: str, feature_id: int):
    bpolys = db_client.get_bpolys_from_db(dataset=dataset, feature_id=feature_id)
    return bpolys
