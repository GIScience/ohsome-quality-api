![](docs/img/oqt_logo.png)

# ohsome quality analyst

## Vision

What is OQT?
* A project that **formalizes the knowledge on OSM data quality** within HeiGIT and the GIScience Research Group.
* A tool that end users, e.g. humanitarian organisations and public administration, can use to get information on the **quality of OSM data for their specific region and use-case**.
* A **web app** that builds upon the existing infrastructure, especially [ohsomeHeX](https://ohsome.org/apps/osm-history-explorer) and the [ohsome dashboard](https://ohsome.org/apps/dashboard).
* A **data integration tool**, that brings together the implementation of a variety of intrinsic and extrinsic data quality metrics.


## Overview

Please read following short document to get an overview of OQT: [docs/overview.md](docs/overview.md)


## Installation

End users should use the [website](https://oqt.ohsome.org). Following section is for advanced usage of ohsome quality analyst. To set the project up for development, please refer to [docs/development_setup.md](docs/development_setup.md).

Python 3.8 is required.

Install the ohsome_quality_analyst Python package.

```bash
cd workers
pip install .
```

In addition to installing the Python package, access to the PostGIS database is required. Please reach out if you need one.


## Usage of the API

Head over to [https://oqt.ohsome.org/api/docs#/](https://oqt.ohsome.org/api/docs#/) to explore the API interactively.

The response schema is defined here: [docs/api.md](docs/api.md)


## Usage of the CLI

```bash
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
  list-datasets          List in the Geodatabase available datasets.
  list-indicators        List available indicators and their metadata.
  list-layers            List available layers and how they are definied...
  list-reports           List available reports and their metadata.
```


## Contributing

Please refer to [CONTRIBUTING.md](CONTRIBUTING.md).

Looking to implement a new indicator? Then please have a look at [docs/indicator_creation.md](docs/indicator_creation.md)


## Development Setup

Please refer to [docs/development_setup.md](docs/development_setup.md).

