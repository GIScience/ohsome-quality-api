import uvicorn

from ohsome_quality_analyst.utils.definitions import get_log_config

if __name__ == "__main__":
    uvicorn.run(
        "ohsome_quality_analyst.api:app",
        reload=True,
        reload_dirs=["."],
        log_config=get_log_config(),
    )
