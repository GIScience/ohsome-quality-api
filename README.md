![](docs/img/oqt_logo.png)

# ohsome quality analyst

[![build status](https://jenkins.ohsome.org/buildStatus/icon?job=ohsome-quality-analyst/main)](https://jenkins.ohsome.org/blue/organizations/jenkins/ohsome-quality-analyst/activity/?branch=main)
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=ohsome-quality-analyst&metric=alert_status)](https://sonarcloud.io/dashboard?id=ohsome-quality-analyst)
[![LICENSE](https://img.shields.io/badge/license-AGPL--v3-orange)](LICENSE.txt)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Foqt.ohsome.org)](https://oqt.ohsome.org)
[![status: active](https://github.com/GIScience/badges/raw/master/status/active.svg)](https://github.com/GIScience/badges#active)

The ohsome quality analyst (OQT) computes and provides data quality estimations (indicators) for OpenStreetMap.

The software is developed by [Heidelberg Institute for Geoinformation Technology (HeiGIT)](https://heigit.org/) and based on the [ohsome platform](https://heigit.org/big-spatial-data-analytics-en/ohsome/).

## Blog

The following blog posts give insight into OQT:
- [Introducing the ohsome quality analyst (OQT)](https://heigit.org/introducing-the-ohsome-quality-analyst-oqt)
- [Behind the scenes of the ohsome quality analyst (OQT)](https://heigit.org/behind-the-scenes-of-the-ohsome-quality-analyst-oqt)
- as well as other [blog posts about OQT](https://heigit.org/tag/oqt-en)

## Website

The easiest access to quality estimations is through our [website](https://oqt.ohsome.org). There reports with pre-computed indicators can be accessed for a selection of regions made by the OQT team. Currently it is not possible to upload custom areas-of-interest (AOIs) and compute report or indicators for those.

## API

Our [API](https://oqt.ohsome.org/api/docs) offers the most flexible way to request quality estimations from OQT. It is possible to request pre-computed indicators for a selection of regions made by the OQT team as well as for your own areas-of-interest (GeoJSON). At the moment a limitation on the area of the input geometry exists. The API will return a GeoJSON Feature. This GeoJSON will preserve both the `geometry` and `property` field of the input GeoJSON Feature. The data and results of a computed indicator are written to the `properties` field of the resulting GeoJSON Feature.

 For more information check out the interactive [API documentation](https://oqt.ohsome.org/api/docs), our static [documentation](docs/api.md) and our interactive [examples](https://github.com/GIScience/oqt-examples) using Python and Jupyter Notebooks.

## CLI

It is also possible to set up OQT on your local machine and use the provided CLI. This is the most flexible way but some technical knowledge is required to set it up. For now please refer to the [development setup documentation](docs/development_setup.md) on how to set up OQT locally on your machine. After installation of the `ohsome_quality_analyst` Python package run `oqt --help` for documentation about the CLI.

## Contributing

Contributions of any form are more than welcome! Please take a look at our [contributing
guidelines](CONTRIBUTING.md) for details on our git workflow and style guide.
on.

Are you looking to implement a new indicator? Then please have a look at [docs/indicator_creation.md](/docs/indicator_creation.md)

Are you looking to add a new layer? Then please have a look at [docs/layer.md](/docs/layer.md)

## Development

Please refer to [this document](docs/development_setup.md](/docs/development_setup.md) for a guide on how to setup OQT for development.

## Components

Following diagram gives an overview of the OQT components:

![](/docs/img/UML-Component-Diagram.png)
