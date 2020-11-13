from fastapi import FastAPI

from ohsome_quality_tool import oqt
from ohsome_quality_tool.utils import geodatabase

app = FastAPI()


@app.get("/test/{indicator}")
async def get_test(indicator: str):
    return {"indicator_name": indicator}


@app.get("/static_indicator/{indicator}")
async def get_static_indicator(indicator: str, dataset: str, feature_id: int):
    results = oqt.get_static_indicator(
        indicator_name=indicator, dataset=dataset, feature_id=feature_id
    )
    return results


@app.get("/static_report/{report}")
async def get_static_report(report: str, dataset: str, feature_id: int):
    results = oqt.get_static_report(
        report_name=report, dataset=dataset, feature_id=feature_id
    )
    return results


@app.get("/geometries/{dataset}")
async def get_bpolys_from_db(dataset: str, feature_id: int):
    bpolys = geodatabase.get_bpolys_from_db(dataset=dataset, feature_id=feature_id)
    return bpolys
