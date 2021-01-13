# Overview
This document should give you an overview on what document what is currently working and what is still missing. It covers the following parts:

* Indicators
* Reports
* Website
* API
* Command Line Interface

## Indicators
So far we have implemented a few indicators which are either intrinsic or rely on extrinsic data sets.

Extrinsic indicators:
* Global Human Settlement Layer Comparison
* Global Urban Footprint Comparison

Intrinsic Indicators:
* Mapping Saturation
* Points-of-interest Density
* Last Edit

Currently missing:
* All indicators are area based. Hence, they provide a quality estimate for a region and not for single objects in OSM.

## Reports
So far we have implemented a few reports which combine the existing indicators. Currently there are the following:
* Simple Report
* remote mapping report (buildings, roads)
* sketch mapping report

Currently missing:
* For all reports the indicators are aggregated using the same weight. 

## Website
The website can be accessed from within the university network only here: [129.206.4.240/index.html](http://129.206.4.240/index.html). The website relies on the OQT api and currently only queries the `static/report` endpoint.

The website is split up into two main parts, which will be explained in the following:

### Website Part 1
First, the user needs to select an area of interest and a respective data quality report. Currently, the set of available geometries has been picked manually and is defined in a [geojson file](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-tool/-/blob/master/website/website/assets/data/test-regions.geojson).

User can select one of the following reports, which are hardcoded in website code [here](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-tool/-/blob/master/website/website/index.html):
* simple report
* remote mapping report (buildings, roads)
* sketch mapping report

Currently missing:
* users can't upload a geojson file with a custom extent

<img src="img/oqt_website_step1.png" width="450px">

### Website Part 2
The second part visualizes the results of the selected data quality report. This part is split up into two sub-sections:

* overall data quality report (aggregated quality value based on all indicators)
* data quality indicators (quality value for each indicator)

Curently missing:
* the plots are not interactive, but static images

<img src="img/oqt_website_step2.png" width="450px">

## API
The api can be accessed from within the university network only here: [http://129.206.4.240:8080](http://129.206.4.240:8080). There is a [swagger documentation](http://129.206.4.240:8080/docs) as well. 

Using the api one can either retrieve information on pre-processed reports or indicators from a postgres database (`static` endpoints) or dynamically trigger their computation (`dynamic` endpoints). These are the current endpoints:

* `static/indicator/{name}` (get)
* `static/report/{name}` (get and post)
* `dynamic/indicator/{name}` (get)
* `dynamic/report/{name}` (get and post)

It is NOT possible to trigger the pre-processing workflow (e.g. pre-process the mapping saturation indicator for all countries) using the api.

## Command Line Interface
The command line interface offers the biggest flexibility. Using the cli one can retrieve pre-processed report and indicators and trigger their pre-processing or dynamically trigger the calculation of any indicator or report for a custom geojson geometry.

One can get an overview which functions are available when running:
```
oqt --help
```

```
Usage: oqt [OPTIONS] COMMAND [ARGS]...

Options:
  --version      Show the version and exit.
  -v, --verbose  Enable logging.
  --help         Show this message and exit.

Commands:
  get-dynamic-indicator
  get-dynamic-report
  get-static-indicator
  get-static-report
  get-static-report-pdf
  process-all-indicators
  process-indicator
```

Currently missing:
* The results are not exported or saved to a file.
