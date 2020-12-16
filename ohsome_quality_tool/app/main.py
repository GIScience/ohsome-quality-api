import json

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ohsome_quality_tool import oqt
from ohsome_quality_tool.utils import geodatabase

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

response_template = {
    "attribution": {
        "url": "https://ohsome.org/copyrights",
        "text": "© OpenStreetMap contributors",
    },
    "apiVersion": "0.1",
    "metadata": "",
    "result": "",
}


@app.get("/test/{name}")
async def get_test(name: str):
    return {"indicator-name": name}


@app.get("/static/indicator/{name}")
async def get_static_indicator(name: str, dataset: str, feature_id: int):
    results = oqt.get_static_indicator(
        indicator_name=name, dataset=dataset, feature_id=feature_id
    )
    return results


# added for now for testing purposes
@app.get("/dynamic/indicator/{name}")
async def get_dynamic_indicator(name: str, bpolys: str, request: Request):
    bpolys = json.loads(bpolys)
    result, metadata = oqt.get_dynamic_indicator(indicator_name=name, bpolys=bpolys)
    response = response_template
    response["metadata"] = metadata._asdict()
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = result._asdict()

    return response


@app.get("/static/report/{name}")
async def get_static_report(name: str, dataset: str, feature_id: int):
    results = oqt.get_static_report(
        report_name=name, dataset=dataset, feature_id=feature_id
    )
    return results


@app.get("/dynamic/report/{name}")
async def get_dynamic_report(name: str, bpolys: str, request: Request):
    bpolys = json.loads(bpolys)

    print(bpolys)

    result, indicators, metadata = oqt.get_dynamic_report(
        report_name=name, bpolys=bpolys
    )

    print(result, indicators, metadata)

    response = response_template
    response["metadata"] = metadata._asdict()
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = result._asdict()
    response["indicators"] = indicators

    return response


class Item(BaseModel):
    bpolys: str


@app.post("/dynamic/report/{name}")
async def post_dynamic_report(name: str, item: Item, request: Request):
    bpolys = json.loads(item.dict()["bpolys"])
    result, indicators, metadata = oqt.get_dynamic_report(
        report_name=name, bpolys=bpolys
    )

    print(result, indicators, metadata)

    response = response_template
    response["metadata"] = metadata._asdict()
    response["metadata"]["requestUrl"] = request.url._url
    response["result"] = result._asdict()
    response["indicators"] = indicators

    return response


@app.get("/geometries/{dataset}")
async def get_bpolys_from_db(dataset: str, feature_id: int):
    bpolys = geodatabase.get_bpolys_from_db(dataset=dataset, feature_id=feature_id)
    return bpolys
