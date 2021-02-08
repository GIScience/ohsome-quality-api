# Overview
This document should give you an overview on what is already implemented and works, and what is still missing and might 
come in future releases. It covers the following parts:

* Indicators
* Reports
* Website
* API
* Command Line Interface

## Indicators
So far we have implemented a few indicators which are either intrinsic, or rely on extrinsic data sets.

Extrinsic indicators:
* Global human settlement layer comparison
* Global urban footprint comparison

Intrinsic Indicators:
* Mapping saturation
* Points-of-interest density
* Last edit

Currently missing:
* Feature-based indicators, as so far all indicators are area-based, meaning they provide a quality estimation for a 
whole region and not for single OSM features

## Reports
So far we have implemented a few reports, which combine different sets of indicators. Currently there are the following:
* Simple report
* Remote mapping report (buildings, roads)
* Sketch mapping report

Currently missing:
* Definition of individual weights for the indicators, as they are so far aggregated using the same weights

## Website
The website can only be accessed from within the university network here: 
[129.206.4.240/index.html](http://129.206.4.240/index.html). The website relies on the OQT API and currently only 
queries the `static/report` endpoint.

The website is split up into two main parts:

### Website Part 1
First, the user needs to select an area of interest and a respective data quality report. Currently, the set of 
available geometries has been picked manually and is defined in a 
[GeoJSON file](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-analyst/-/blob/master/website/website/assets/data/test_regions.geojson).

The user can select one of the following reports, which are hardcoded in the 
[website code](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/ohsome-quality-analyst/-/blob/master/website/website/index.html):
* Simple report
* Remote mapping report (buildings, roads)
* Sketch mapping report

Currently missing:
* Definition of a custom area of interest, which can be uploaded for example as GeoJSON

<img src="img/oqt_website_step1.png" width="450px">

### Website Part 2
The second part visualizes the results of the selected data quality report. This part is split up into two sub-sections:

* Overall data quality report (aggregated quality value based on all indicators)
* Data quality indicators (quality value for each indicator)

Curently missing:
* Interactive plots, as there are only static images visualized in the website at the moment

<img src="img/oqt_website_step2.png" width="450px">

## API
The API can be accessed from within the university network only via this address: 
[http://129.206.4.240:8080](http://129.206.4.240:8080). 
There is also a [swagger documentation](http://129.206.4.240:8080/docs) available. 

Using the API one can either retrieve information on pre-processed reports, or indicators from a postgres database 
(`static` endpoints), or dynamically trigger their computation (`dynamic` endpoints). These are the current endpoints:

* `static/indicator/{name}` (get)
* `static/report/{name}` (get and post)
* `dynamic/indicator/{name}` (get)
* `dynamic/report/{name}` (get and post)

It is NOT possible to trigger the pre-processing workflow (e.g. pre-process the mapping saturation indicator for all 
countries) using the API.

## Command Line Interface
The command line interface offers the biggest flexibility. Using the cli one can retrieve pre-processed reports and 
indicators, trigger their pre-processing, or dynamically trigger the calculation of any indicator or report for a 
custom GeoJSON geometry.

One can get an overview on which functions are available when running:
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
* Exporting or saving the results to a file
