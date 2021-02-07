import json
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ohsome_quality_analyst import oqt
from ohsome_quality_analyst.geodatabase import client as db_client
from ohsome_quality_analyst.utils.helper import name_to_lower_camel

RESPONSE_TEMPLATE = {
    "attribution": {
        "url": "https://ohsome.org/copyrights",
        "text": "© OpenStreetMap contributors",
    },
    "apiVersion": "0.1",
}

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


class ReportParameters(BaseModel):
    bpolys: Optional[str] = None
    dataset: Optional[str] = None
    featureId: Optional[str] = None


@app.get("/indicator/{name}")
async def get_indicator(
    name: str,
    request: Request,
    layerName: str,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    featureId: Optional[str] = None,
):
    # TODO: Error handling should happen in oqt.create_indicator
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and featureId is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    indicator = oqt.create_indicator(name, layerName, bpolys, dataset, featureId)
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(indicator.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["metadata"].pop("result_description", None)
    response["metadata"].pop("label_description", None)
    response["layer"] = vars(indicator.layer)
    response["result"] = vars(indicator.result)
    response["result"]["label"] = str(indicator.result.label)
    return response


@app.post("/indicator/{name}")
async def post_indicator(name: str, request: Request, item: IndicatorParameters):
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("featureId", None)
    layer_name = item.dict().get("layerName", None)
    # TODO: Error handling should happen in oqt.create_indicator
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and feature_id is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    indicator = oqt.create_indicator(name, layer_name, bpolys, dataset, feature_id)
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(indicator.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["metadata"].pop("result_description", None)
    response["metadata"].pop("label_description", None)
    response["layer"] = vars(indicator.layer)
    response["result"] = vars(indicator.result)
    response["result"]["label"] = str(indicator.result.label)
    return response


@app.get("/report/{name}")
async def get_report(
    name: str,
    request: Request,
    bpolys: Optional[str] = None,
    dataset: Optional[str] = None,
    featureId: Optional[str] = None,
):
    # TODO: Error handling should happen in oqt.create_report
    if bpolys:
        bpolys = json.loads(bpolys)
    elif dataset is None and featureId is None:
        raise ValueError("Provide either bpolys or dataset and feature_id")
    report = oqt.create_report(
        name, bpolys=bpolys, dataset=dataset, feature_id=featureId
    )
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(report.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["metadata"].pop("label_description", None)
    response["result"] = vars(report.result)
    response["result"]["label"] = str(report.result.label)
    response["indicators"] = []
    for indicator in report.indicators:
        metadata = vars(indicator.metadata)
        metadata.pop("result_description", None)
        metadata.pop("label_description", None)
        layer = (vars(indicator.layer),)
        result = vars(indicator.result)
        result["label"] = str(indicator.result.label)
        indicator_name = name_to_lower_camel(metadata["name"])
        response["indicators"].append(
            {
                indicator_name: {
                    "metadata": metadata,
                    "layer": layer,
                    "result": result,
                }
            }
        )
    return response


@app.post("/report/{name}")
async def post_report(name: str, request: Request, item: ReportParameters):
    bpolys = item.dict().get("bpolys", None)
    dataset = item.dict().get("dataset", None)
    feature_id = item.dict().get("featureId", None)
    # TODO: Error handling should happen in oqt.create_report
    if bpolys:
        bpolys = json.loads(bpolys)
    report = oqt.create_report(
        name, bpolys=bpolys, dataset=dataset, feature_id=feature_id
    )
    response = RESPONSE_TEMPLATE
    response["metadata"] = vars(report.metadata)
    response["metadata"]["requestUrl"] = request.url._url
    response["metadata"].pop("label_description", None)
    response["result"] = vars(report.result)
    response["result"]["label"] = str(report.result.label)
    response["indicators"] = []
    for indicator in report.indicators:
        metadata = vars(indicator.metadata)
        metadata.pop("result_description", None)
        metadata.pop("label_description", None)
        layer = vars(indicator.layer)
        result = vars(indicator.result)
        result["label"] = str(indicator.result.label)
        indicator_name = name_to_lower_camel(metadata["name"])
        response["indicators"].append(
            {
                indicator_name: {
                    "metadata": metadata,
                    "layer": layer,
                    "result": result,
                }
            }
        )
    return response


@app.get("/geometries/{dataset}")
async def get_bpolys_from_db(dataset: str, featureId: int):
    bpolys = db_client.get_bpolys_from_db(dataset=dataset, feature_id=featureId)
    return bpolys
