# Deployment using Docker

Build and run Services:

```bash
cd /opt/ohsome-quality-tools/
git pull
docker-compose -f docker-compose.yml -f docker-compose.production.yml up --build --force-recreate -d
```

Trigger a CLI command:

```bash
docker-compose run oqt-workers .local/bin/oqt --verbose create-indicator -i GhsPopComparison --infile data/heidelberg_altstadt.geojson
```

Calculate all indicators for a specific dataset (This will only work if those results are not yet in the database.):

```bash
docker-compose run oqt-workers .local/bin/oqt --verbose create-indicators-for-dataset --dataset-name "test_regions"
```

> NOTE: For the production setup of the Geodatabase please refer to [database/README.md](database/README.md).
