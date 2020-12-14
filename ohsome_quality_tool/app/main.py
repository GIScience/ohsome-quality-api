import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ohsome_quality_tool import oqt
from ohsome_quality_tool.utils import geodatabase

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


@app.get("/test/{indicator_name}")
async def get_test(indicator_name: str):
    return {"indicator_name": indicator_name}


@app.get("/static_indicator/{indicator_name}")
async def get_static_indicator(indicator_name: str, dataset: str, feature_id: int):
    results = oqt.get_static_indicator(
        indicator_name=indicator_name, dataset=dataset, feature_id=feature_id
    )
    return results


# added for now for testing purposes
@app.get("/dynamic_indicator/{indicator_name}")
async def get_dynamic_indicator(indicator_name: str, bpolys: str):
    bpolys = json.loads(bpolys)
    result, metadata = oqt.get_dynamic_indicator(
        indicator_name=indicator_name, bpolys=bpolys
    )
    response = response_template
    response["metadata"] = metadata._asdict()
    response["result"] = result._asdict()

    return response


@app.get("/static_report/{report_name}")
async def get_static_report(report_name: str, dataset: str, feature_id: int):
    results = oqt.get_static_report(
        report_name=report_name, dataset=dataset, feature_id=feature_id
    )
    return results


@app.get("/dynamic_report/{report_name}")
async def get_dynamic_report(report_name: str, bpolys: str):
    bpolys = json.loads(bpolys)

    print(bpolys)

    result, indicators, metadata = oqt.get_dynamic_report(
        report_name=report_name, bpolys=bpolys
    )

    print(result, indicators, metadata)

    response = response_template
    response["metadata"] = metadata._asdict()
    response["result"] = result._asdict()
    response["indicators"] = indicators

    return response


class Item(BaseModel):
    bpolys: str


@app.post("/dynamic_report/{report_name}")
async def post_dynamic_report(report_name: str, item: Item):
    bpolys = json.loads(item.dict()["bpolys"])
    result, indicators, metadata = oqt.get_dynamic_report(
        report_name=report_name, bpolys=bpolys
    )

    print(result, indicators, metadata)

    response = response_template
    response["metadata"] = metadata._asdict()
    response["result"] = result._asdict()
    response["indicators"] = indicators

    return response


@app.get("/geometries/{dataset}")
async def get_bpolys_from_db(dataset: str, feature_id: int):
    bpolys = geodatabase.get_bpolys_from_db(dataset=dataset, feature_id=feature_id)
    return bpolys
