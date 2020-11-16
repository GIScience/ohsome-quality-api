import os

# get Postgres config from environment
POSTGRES_DB = os.getenv("POSTGRES_DB", default="oqt")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", default="oqt_workers")

OHSOME_API = os.getenv("OHSOME_API", default="https://api.ohsome.org/v1/")
