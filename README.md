![](docs/img/oqt_logo.png)


# ohsome quality analyst

[![build status](https://jenkins.ohsome.org/buildStatus/icon?job=ohsome-quality-analyst/main)](https://jenkins.ohsome.org/blue/organizations/jenkins/ohsome-quality-analyst/activity/?branch=main)
[![Sonarcloud Status](https://sonarcloud.io/api/project_badges/measure?project=ohsome-quality-analyst&metric=alert_status)](https://sonarcloud.io/dashboard?id=ohsome-quality-analyst)
[![LICENSE](https://img.shields.io/badge/license-AGPL--v3-orange)](LICENSE.txt)
[![Website](https://img.shields.io/website?url=https%3A%2F%2Foqt.ohsome.org)](https://oqt.ohsome.org)
[![status: active](https://github.com/GIScience/badges/raw/master/status/active.svg)](https://github.com/GIScience/badges#active)


## Vision

What is OQT?
* A project that **formalizes the knowledge on OSM data quality** within HeiGIT and the GIScience Research Group.
* A tool that end users, e.g. humanitarian organisations and public administration, can use to get information on the **quality of OSM data for their specific region and use-case**.
* A **web app** that builds upon the existing infrastructure, especially [ohsomeHeX](https://ohsome.org/apps/osm-history-explorer) and the [ohsome dashboard](https://ohsome.org/apps/dashboard).
* A **data integration tool**, that brings together the implementation of a variety of intrinsic and extrinsic data quality metrics.


## Blog

The following blog posts give insight into OQT and describe how you can use it:
 * [Introducing the ohsome quality analyst (OQT)](https://heigit.org/introducing-the-ohsome-quality-analyst-oqt)
 * [Behind the scenes of the ohsome quality analyst (OQT)](https://heigit.org/behind-the-scenes-of-the-ohsome-quality-analyst-oqt)
 * as well as other [blog posts about OQT](https://heigit.org/tag/oqt-en)


## Usage

There are three ways to use OQT.

> Note: To set the project up for development, please refer to [docs/development_setup.md](/docs/development_setup.md).


### Website

Through the OQT [Website](https://oqt.ohsome.org) indicators and reports can be requested for regions definied by the OQT team. Those are pre-computed and can be retrieved very fast.


### API

Head over to [https://oqt.ohsome.org/api/docs](https://oqt.ohsome.org/api/docs) to explore the OQT API interactively.

The response schema is defined here: [docs/api.md](/docs/api.md)


### CLI

To use the OQT CLI the `ohsome_quality_analyst` Python package needs to be installed and configured. Additionally access to the OQT database is required. Please reach out if you need one.

Python 3.8 is required.

```bash
$ cd workers
$ pip install .
$ # Configure OQT
$ oqt --help
Usage: oqt [OPTIONS] COMMAND [ARGS]...

Options:
  --version    Show the version and exit.
  -q, --quiet  Disable logging.
  --help       Show this message and exit.

Commands:
  create-all-indicators  Create all indicators for a specified dataset.
  create-indicator       Create an Indicator and print results to stdout.
  create-report          Create a Report and print results to stdout.
  list-datasets          List available datasets.
  list-indicators        List available indicators and their metadata.
  list-layers            List available layers and how they are definied...
  list-regions           List available regions.
  list-reports           List available reports and their metadata.
```


## OQT Components

This diagram gives an overview of the OQT components:

![](/docs/img/UML-Component-Diagram.png)


## Contributing

Please refer to [CONTRIBUTING.md](/CONTRIBUTING.md).

Looking to implement a new indicator? Then please have a look at [docs/indicator_creation.md](/docs/indicator_creation.md)

Looking to add a new layer to run your analysis with? Then please have a look at [docs/layer.md](/docs/layer.md)

## Development Setup

Please refer to [docs/development_setup.md](/docs/development_setup.md).
