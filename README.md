![oqt_header](logo/oqt_header.png)

# Proof of Concept for Ohsome Quality Tool

## Vision
What is OQT?
* A project that **formalizes the knowledge on OSM data quality** within HeiGIT and the GIScience Research Group
* A tool that end users, e.g. humanitarian organisations and public administration, can use to get information on the **quality of OSM data for their specific region and use-case**.
* A **web app** that builds upon the existing infrastructure, especially ohsome-hex and the ohsome dashboard
* A **data integration tool**, that brings together the implementation of a variety of intrinsic and extrinsic data quality metrics

For more information check [Confluence](https://confluence.gistools.geog.uni-heidelberg.de/display/oshdb/The+ohsome+Quality+Tool).

## Quickstart
Run the following lines to use the tool from a command line. Make sure that you have `Python3.8` and `poetry` installed on the system level already.

```
git clone https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-tool.git
cd ohsome-quality-tool
poetry install
poetry shell
```

### Command Line Interface
Run the following line to get an overview:
```
oqt --help 
```

Run the following line to derive the `GHSPOP_COMPARISON` indicator:
```
oqt --verbose get-dynamic-indicator -i GHSPOP_COMPARISON --infile data/heidelberg_altstadt.geojson 
```

Run the following line to derive the `SKETCHMAP_FITNESS` report:
```
oqt --verbose get-dynamic-report -r SKETCHMAP_FITNESS --infile data/heidelberg_altstadt.geojson
```

### API
Run the following line to start the server:
```
uvicorn ohsome_quality_tool.app.main:app --reload
```

Go to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) and check out the endpoints.


### Docker
You can also run the tool using docker, e.g. if you have problems installing on Windows. For now this will run the api at http://127.0.0.1:8000/docs. The website will be served at http://127.0.0.1:8080. This should be enough to test that the installation worked.
```
docker-compose up -d oqt-workers oqt-website
```

You can run a cli command using the docker image like this:
```
docker-compose run oqt-workers oqt --verbose get-dynamic-indicator -i GHSPOP_COMPARISON --infile data/heidelberg_altstadt.geojson
```

## Development
For development setup and contributing setup please have look at [CONTRIBUTING.md](CONTRIBUTING.md)

![components](docs/componet_diagram_new.png)
