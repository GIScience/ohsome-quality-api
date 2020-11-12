from fastapi import FastAPI

app = FastAPI()


@app.get("/indicator/{indicator_name}")
async def read_item(indicator_name: str):
    return {"indicator_name": indicator_name}
