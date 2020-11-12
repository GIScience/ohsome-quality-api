from fastapi import FastAPI

from ohsome_quality_tool import oqt

app = FastAPI()


@app.get("/test/{indicator}")
async def get_test(indicator: str):
    return {"indicator_name": indicator}


@app.get("/static_indicator/{indicator}")
async def get_static_indicator(indicator: str, area_filter: str):
    oqt.get_static_indicator(indicator=indicator, area_filter=area_filter)
    return {"indicator_name": indicator}


@app.get("/static_report/{report}")
async def get_static_report(report: str, area_filter: str):
    oqt.get_static_report(report=report, area_filter=area_filter)
    return {"report_name": report}
