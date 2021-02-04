# Deployment using Docker

A running Geodatabase setup is required. Currently this setup is not supported for docker-compose. Please see [database/README.md](database/README.md) for more information on the setup which is currently used in production.

Build and run the API and the website.

```bash
cd /opt/ohsome-quality-tools/
git pull
docker-compose -f docker-compose.yml -f docker-compose.production.yml up --build --force-recreate -d
```

Calculate all indicators for a specific dataset (This will only work if those results are not yet in the database.):

```bash
docker-compose exec oqt-workers .local/bin/oqt --verbose create-indicators-for-dataset --dataset-name "test_regions"
```
