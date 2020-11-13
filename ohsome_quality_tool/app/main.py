from fastapi import FastAPI

from ohsome_quality_tool import oqt

app = FastAPI()


@app.get("/test/{indicator}")
async def get_test(indicator: str):
    return {"indicator_name": indicator}


@app.get("/static_indicator/{indicator}")
async def get_static_indicator(indicator: str, table: str, feature_id: int):
    results = oqt.get_static_indicator(
        indicator_name=indicator, table=table, feature_id=feature_id
    )
    return results


@app.get("/static_report/{report}")
async def get_static_report(report: str, table: str, feature_id: int):
    results = oqt.get_static_report(
        report_name=report, table=table, feature_id=feature_id
    )
    return results
