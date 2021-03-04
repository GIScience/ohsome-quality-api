import uvicorn

from ohsome_quality_analyst.utils.definitions import load_logging_config

if __name__ == "__main__":
    uvicorn.run(
        "ohsome_quality_analyst.api:app",
        port=8080,
        reload=True,
        reload_dirs=["."],
        log_config=load_logging_config(),
    )
