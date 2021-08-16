![](docs/img/oqt_logo.png)


# ohsome quality analyst

[![build status](https://jenkins.ohsome.org/buildStatus/icon?job=ohsome-quality-analyst/main)](https://jenkins.ohsome.org/blue/organizations/jenkins/ohsome-quality-analyst/activity/?branch=main)
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=ohsome-quality-analyst&metric=alert_status)](https://sonarcloud.io/dashboard?id=ohsome-quality-analyst)
[![LICENSE](https://img.shields.io/badge/license-AGPL--v3-orange)](LICENSE.txt)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Foqt.ohsome.org)](https://oqt.ohsome.org)
[![status: active](https://github.com/GIScience/badges/raw/master/status/active.svg)](https://github.com/GIScience/badges#active)

The ohsome quality analyst (OQT) is a software developed by [Heidelberg Institute for Geoinformation Technology (HeiGIT)](https://heigit.org/) and based on the [ohsome platform](https://heigit.org/big-spatial-data-analytics-en/ohsome/). The main purpose is to compute and provide quality estimations of OpenStreetMap (OSM) data.


## Blog

The following blog posts give insight into OQT:
- [Introducing the ohsome quality analyst (OQT)](https://heigit.org/introducing-the-ohsome-quality-analyst-oqt)
- [Behind the scenes of the ohsome quality analyst (OQT)](https://heigit.org/behind-the-scenes-of-the-ohsome-quality-analyst-oqt)
- as well as other [blog posts about OQT](https://heigit.org/tag/oqt-en)


## OQT Components

This diagram gives an overview of the OQT components:

![](/docs/img/UML-Component-Diagram.png)


## Usage

OQT can be used in three ways with various degree of usability and flexibility:
1. Interactive access through the *website* (Highest usability; Lowest flexibility)
2. Making requests to the *REST API*
3. Usage of the Command-Line-Interface (*CLI*) (Lowest usability; Highest flexibility)

The easiest access to quality reports is through the OQT [website](https://oqt.ohsome.org). There reports with pre-computed indicators can be accessed for a selection of regions made by the OQT team. But it is not possible to upload custom areas-of-interest (AOIs) and compute report or indicators for those.

Requests for individual indicators as well as reports can be made to the OQT [API](https://oqt.ohsome.org/api/docs). Retrievable are pre-computed indicators for selected regions (Parameters `dataset=regions` and `featureId`) as well as for custom AOIs (Parameter `bpolys`). The major drawback is the limitation of the input geometry size. For more information check out the interactive [API documentation](https://oqt.ohsome.org/api/docs).

The last way to use OQT is by setting up OQT on your local machine and use the provided CLI. This is the most flexible way but some technical knowledge is required to set it up. For now please refer to the [development setup documentation](/docs/development_setup.md) on how to set up OQT locally on your machine. After installation of the `ohsome_quality_analyst` Python package run `oqt --help` for documentation about the CLI.


The API as well as the CLI will return a GeoJSON Feature. This GeoJSON will preserve both the `geometry` and `property` field of the input GeoJSON Feature. The data and results of the indicator or report and its associated indicators are written to the `property` field in a flat hierarchy of the resulting GeoJSON Feature.


## Contributing

Please refer to [CONTRIBUTING.md](/CONTRIBUTING.md).

Looking to implement a new indicator? Then please have a look at [docs/indicator_creation.md](/docs/indicator_creation.md)


## Development Setup

Please refer to [docs/development_setup.md](/docs/development_setup.md).
