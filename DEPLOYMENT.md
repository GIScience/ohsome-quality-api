# Deployment using Docker

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Trigger a CLI command:

```bash
docker-compose run oqt-workers oqt --verbose create-indicator -i GhsPopComparison --infile data/heidelberg_altstadt.geojson
```

> NOTE For the production setup of the Geodatabase please refer to [database/README.md](database/README.md).
