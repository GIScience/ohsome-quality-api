# Changelog

## Current Main

### Breaking Changes

- change API parameter names for POST requests from snake case to lower hyphen ([#398])
- change indicator and report keys from lower camel case to lower hyphen ([#398])
- rename API parameter `layerKey` and `layer` to `topic` ([#501])
- remove GHS POP Comparison indicators: `ghs_pop_comparison_buildings` and `ghs_pop_comparison_roads` ([#515])
- remove JRC related layers and report `jrc_requirements` ([#503])
- rename `TagsRatio` indicator to `attribute-completeness` ([#500])
- requests to the API endpoint `/indicator` for a custom layer/topic need an additional field `key` of type string ([#517])
- remove GET request for indicators and reports ([#516])

### Bug Fixes

- mapping-saturation: add missing edge case detection for too few data points. ([#512])
- doctors topic: use correct filter ([#540])

### New Features

- disable size limit for Mapping Saturation ([#498])
- add `project` attribute to topics ([#504])
- layer/topic are now pydantic models instead of dataclasses ([#517])
- add plot creation via plotly to `MappingSaturation` indicator ([#499])
- api: add `/metadata/topic` endpoint ([#519])
- api: add `/metadata/indicators` endpoint ([#533])
- api: add `/metadata/reports` endpoint ([#545])
- api: add `/metadata` endpoint ([#545])

### Other Changes

- fix pre-commit hooks ([#482])
- update asyncpg from 0.25 to 0.27 ([#481])
- refactor(db): remove artifacts as well as old init scripts and restructure directories ([#388])
- overhaul docker compose setup ([#483])
- build(deps): update FastAPI to version 0.92.0 ([#488])
- topics: tidy up and fix filters of core topic definitions ([#520])
- refactor(topic): rename layer to topic ([#521])
- refactor(topic): move `base/topic.py` to `topics/models.py` and `layer_defintions.yaml` to `topics/presets.yaml` ([#523])
- refactor: move base classes to related modules ([#524])
- refactor: move topic-indicator-combinations to topic definition ([#528])
- fix: remove unnecessary newlines from API output and internal definitions ([#529])
- build: update minimal python version to 3.10 ([#531])
- build: update dev dependencies ([#531])
- mapping-saturation: substitute matplotlib SVG with plotly SVG ([#536])
- api: fix attribution URL path ([#543])

### How to Upgrade

- rename indicator keys from camel case to lower hyphen ([#398]): E.g. `MappingSaturation` to `mapping-saturation`
- rename API parameters for POST requests from camel case to lower hyphen ([#398])
- rename API parameter `layerKey` and `layer` to `topic` ([#501])
- for requests to the API endpoint `/indicator` for a custom topic add an additional field `key` of type string ([#517])
  - E.g. `{"name": "mapping-saturation", "bpolys": {...}, "topic": {"key": "my-key", "name": "my-name", "description": "my-description", "data": {...}}"`
- API endpoint `/indicator` and `/report` do not support GET request anymore. Change request to those endpoints to use the POST method ([#516]).

| old API parameter | new API parameter |
| ---               | ---               |
| `layerKey`        | `topic`           |
| `includeSvg`      | `include-svg`     |
| `includeHtml`     | `include-html`    |
| `featureId`       | `feature-id`      |
| `fidField`        | `indicators`      |

[#388]: https://github.com/GIScience/ohsome-quality-analyst/pull/388
[#398]: https://github.com/GIScience/ohsome-quality-analyst/pull/398
[#481]: https://github.com/GIScience/ohsome-quality-analyst/pull/481
[#482]: https://github.com/GIScience/ohsome-quality-analyst/pull/482
[#483]: https://github.com/GIScience/ohsome-quality-analyst/pull/483
[#488]: https://github.com/GIScience/ohsome-quality-analyst/pull/488
[#498]: https://github.com/GIScience/ohsome-quality-analyst/pull/498
[#499]: https://github.com/GIScience/ohsome-quality-analyst/pull/499
[#500]: https://github.com/GIScience/ohsome-quality-analyst/pull/500
[#501]: https://github.com/GIScience/ohsome-quality-analyst/pull/501
[#503]: https://github.com/GIScience/ohsome-quality-analyst/pull/503
[#504]: https://github.com/GIScience/ohsome-quality-analyst/pull/504
[#512]: https://github.com/GIScience/ohsome-quality-analyst/pull/512
[#515]: https://github.com/GIScience/ohsome-quality-analyst/pull/515
[#516]: https://github.com/GIScience/ohsome-quality-analyst/pull/516
[#517]: https://github.com/GIScience/ohsome-quality-analyst/pull/517
[#519]: https://github.com/GIScience/ohsome-quality-analyst/pull/519
[#520]: https://github.com/GIScience/ohsome-quality-analyst/pull/520
[#521]: https://github.com/GIScience/ohsome-quality-analyst/pull/521
[#523]: https://github.com/GIScience/ohsome-quality-analyst/pull/523
[#524]: https://github.com/GIScience/ohsome-quality-analyst/pull/524
[#528]: https://github.com/GIScience/ohsome-quality-analyst/pull/528
[#529]: https://github.com/GIScience/ohsome-quality-analyst/pull/529
[#531]: https://github.com/GIScience/ohsome-quality-analyst/pull/531
[#533]: https://github.com/GIScience/ohsome-quality-analyst/pull/533
[#536]: https://github.com/GIScience/ohsome-quality-analyst/pull/536
[#540]: https://github.com/GIScience/ohsome-quality-analyst/issues/540
[#543]: https://github.com/GIScience/ohsome-quality-analyst/pull/543
[#545]: https://github.com/GIScience/ohsome-quality-analyst/pull/545

## 0.14.2

### Bug Fixes

- currentness: add appropriate timeout for ohsome API metadata requests ([#537])

[#537]: https://github.com/GIScience/ohsome-quality-analyst/issues/537

## 0.14.1

### Bug Fixes

- mapping-saturation: allow result value above 100% ([#479])

[#479]: https://github.com/GIScience/ohsome-quality-analyst/pull/479

## 0.14.0

### Bug Fixes

- fix wrong ratio_filter in layer `building_count` ([#457])
- Reports with only undefined indicators are now labeled undefined too ([#456])
- fix broken link to doc in README ([#466])
- `FoodRelatedReport` now uses red & undefined blocking ([#468])

### New Features

- add new layers `fire_station_count` and `hospitals_count` ([#442])
- Add new layers related to food environment ([#455])
- Add new report `FoodRelatedReport` ([#455])
- add new layers `schools`, `kindergartens`, `clinics`, `doctors`, `bus_stops`, `tram_stops`, `subway_stations`, `marketsplaces`. `parks`, `forests`, `fitness_centres` and `supermarkets` ([#444])

### Other Changes

- remove upper Python version requirement limitation. Minimum Python version is 3.8. ([#465])
- update dependencies ([#465])

[#442]: https://github.com/GIScience/ohsome-quality-analyst/pull/442
[#444]: https://github.com/GIScience/ohsome-quality-analyst/pull/444
[#455]: https://github.com/GIScience/ohsome-quality-analyst/pull/455
[#456]: https://github.com/GIScience/ohsome-quality-analyst/pull/456
[#457]: https://github.com/GIScience/ohsome-quality-analyst/pull/457
[#465]: https://github.com/GIScience/ohsome-quality-analyst/pull/465
[#466]: https://github.com/GIScience/ohsome-quality-analyst/pull/466
[#468]: https://github.com/GIScience/ohsome-quality-analyst/pull/468


## 0.13.0

### Bug Fixes

- Fix patch colorization of Currentness indicator plot ([#432])
- Rename duplicated layer name `Major Roads` to `Major Roads Count` and `Major Roads Length`. Results are stored in database using the layer name as part of the primary key. ([#438])
- Reports take result class of indicators into account ([#372] [#369])

### New features

- Substitute result values of reports by introducing a result class value ([#372])

### Breaking Changes

- Change default data directory to be in workers directory ([#312])

### Other Changes

- Move example rasters of data directory to test fixtures ([#312])

[#312]: https://github.com/GIScience/ohsome-quality-analyst/pull/312
[#372]: https://github.com/GIScience/ohsome-quality-analyst/pull/372
[#432]: https://github.com/GIScience/ohsome-quality-analyst/pull/432
[#438]: https://github.com/GIScience/ohsome-quality-analyst/pull/438


## 0.12.0

### Breaking Changes

- Rename layer `ideal_vgi_infrastructure` to `infrastructure_lines` ([#416] [#426])

### New Features

- Improve Currentness indicator ([#274])
- Add new report `MultilevelCurrentness` ([#403])
- Add MapAction priority countries to database ([#427] [#428])

[#274]: https://github.com/GIScience/ohsome-quality-analyst/pull/274
[#403]: https://github.com/GIScience/ohsome-quality-analyst/pull/403
[#416]: https://github.com/GIScience/ohsome-quality-analyst/pull/416
[#426]: https://github.com/GIScience/ohsome-quality-analyst/pull/426
[#427]: https://github.com/GIScience/ohsome-quality-analyst/pull/427
[#428]: https://github.com/GIScience/ohsome-quality-analyst/pull/428


## 0.11.0

### Breaking Changes

- Make inclusion of indicator data in response optional ([#370])
- Per default properties of the GeoJSON response are not flat ([#375])
- Remove project specific reports `JrcRequirements`, `SketchmapFitness`, and `MapActionPoc` from the website ([#382])
- Rename API query parameter `layerName` to `layerKey` and API endpoint `listLayerNames` to `listLayerKeys` ([#376])
- Rename endpoints for listing of indicator, report, layer, dataset and fid-field names ([#397])
- Rename environment variable `OHSOME_API` to `OQT_OHSOME_API` ([#255])

### Bug Fixes

- Fix indicator description field of GeoJSON properties ([#396])

### New Features

- Add new representative report `RoadReport` ([#357])
- Add new representative report `BuildingReport` ([#356])
- Add ratio filter to `building_count` layer ([#356])
- Configure OQT using files or environment variables ([#255])
- Generalize result values of all Indicators by introducing a result class value ([#369])

### Other Changes

- Remove unused report `RemoteMappingLevelOne` ([#380])
- Substitute Simple Report with a Report named Minimal for testing purposes ([#342] [#385])
- Add a minimal Indicator for testing purposes ([#383])
- Remove database scripts ([#392])
- fix: building completeness figure  ([#410])

### How to Upgrade

- Reports `JrcRequirements`, `SketchmapFitness`, and `MapActionPoc` are not accessibly via the website anymore. If you want to access those reports please use the API.
- To continue to retrieve the properties of the GeoJSON API response as flat list, you need to set the API request parameter `flatten` to `True` ([#375])
- To continue to retrieve additional data of an Indicator or Report provided in an API response, you need to set the API request parameter `include_data` to `True` ([#370])
- Rename environment variable `OHSOME_API`  `OQT_OHSOME_API` ([#255])
- Make sure to rename the API query parameter `layerName` to `layerKey` and API endpoint `listLayerNames` to `listLayerKeys` ([#376])
- If you run your own database, please delete the result table before upgrading ([#369])
- Rename endpoints ([#397]):

| old                          | new                            |
| ---                          | ---                            |
| `indicatorLayerCombinations` | `indicator-layer-combinations` |
| `indicatorNames`             | `indicators`                   |
| `datasetNames`               | `datasets`                     |
| `layerNames`                 | `layers`                       |
| `reportNames`                | `reports`                      |
| `fidFields`                  | `fid-fields`                   |

[#255]: https://github.com/GIScience/ohsome-quality-analyst/pull/255
[#342]: https://github.com/GIScience/ohsome-quality-analyst/pull/342
[#356]: https://github.com/GIScience/ohsome-quality-analyst/pull/356
[#357]: https://github.com/GIScience/ohsome-quality-analyst/pull/357
[#369]: https://github.com/GIScience/ohsome-quality-analyst/pull/369
[#370]: https://github.com/GIScience/ohsome-quality-analyst/pull/370
[#375]: https://github.com/GIScience/ohsome-quality-analyst/pull/375
[#376]: https://github.com/GIScience/ohsome-quality-analyst/pull/376
[#380]: https://github.com/GIScience/ohsome-quality-analyst/pull/380
[#382]: https://github.com/GIScience/ohsome-quality-analyst/pull/382
[#383]: https://github.com/GIScience/ohsome-quality-analyst/pull/383
[#385]: https://github.com/GIScience/ohsome-quality-analyst/pull/385
[#392]: https://github.com/GIScience/ohsome-quality-analyst/pull/392
[#396]: https://github.com/GIScience/ohsome-quality-analyst/pull/396
[#397]: https://github.com/GIScience/ohsome-quality-analyst/pull/397
[#410]: https://github.com/GIScience/ohsome-quality-analyst/pull/410


## 0.10.1

### New Features

- Add new report `MulilevelMappingSaturation` ([#379])

[#379]: https://github.com/GIScience/ohsome-quality-analyst/pull/379



## 0.10.0

### Bug Fixes

- Add missing error handling of `RasterDatasetUndefinedError` and `RasterDatasetNotFoundError` to the API ([#298])
- Fix missing HTML generation for Indicators calculated from scratch (`bpolys` parameter) ([#345])
- Fix semaphore instantiation outside of event-loop ([#346])

### New Features

- Add support for `groupBy/boundary` queries to the ohsome API client ([#272])
- Add `flatten` parameter to API request. Make flatten of GeoJSON properties of Indicators and Reports optional ([#303])
- Make calculation of an Indicator for a FeatureCollection or for a Report asynchronous ([#307])
- Add new Indicator which predicts the building area of the AOI using a trained Random Forest Regressor ([#265])
- Add support for `groupBy/boundary` queries to the ohsome API client ([#272])

### Other Changes

- Improve documentation and examples of the API ([#299])
- Factor out template logic to own module ([#302])
- Remove artifacts of database setup for GHSL raster datasets ([#310])
- Add hex-cells at zoom level 12 for Africa to the database ([#314])
- Disable size limit on input AOI if OSM data is provided through a request with a custom Layer object ([#330])

[#265]: https://github.com/GIScience/ohsome-quality-analyst/pull/265
[#272]: https://github.com/GIScience/ohsome-quality-analyst/pull/272
[#298]: https://github.com/GIScience/ohsome-quality-analyst/pull/298
[#299]: https://github.com/GIScience/ohsome-quality-analyst/pull/299
[#302]: https://github.com/GIScience/ohsome-quality-analyst/pull/302
[#303]: https://github.com/GIScience/ohsome-quality-analyst/pull/303
[#307]: https://github.com/GIScience/ohsome-quality-analyst/pull/307
[#310]: https://github.com/GIScience/ohsome-quality-analyst/pull/310
[#314]: https://github.com/GIScience/ohsome-quality-analyst/pull/314
[#330]: https://github.com/GIScience/ohsome-quality-analyst/pull/330
[#345]: https://github.com/GIScience/ohsome-quality-analyst/pull/345
[#346]: https://github.com/GIScience/ohsome-quality-analyst/pull/346


## 0.9.0

### Breaking Changes

- Update `poi` layer based on ([`openpoiservice`]) [#246])
- Remove `ideal_vgi_poi` layer in favor of new `poi` layer ([#246])

### New Features

- Add new parameter `includeHtml` to the API endpoints `/indicator` and `/report` to include a HTML snippets with the results in the response ([#242])
- Add new parameter `layer` containing `name`, `description` and `data` fields to the API endpoint `indicator`. Only available for POST requests. This enables to compute indicators for given data. ([#245])

### Other Changes

- Use ([`rasterstats`]) to provide access to third-party raster datasets stored on disk ([#227])
- Utilize `singledispatch` for `create_indicator` function of the `oqt` module ([#239])
- Add `landmarks` layer [#246])
- Add SHDI to database and add functionality to get SHDI for an AOI by intersection using SQL ([#266])
- Support any dataset, not just "regions" for CLI function `create_all_indicators` ([#254])
- Fix concurrent execution of CLI function `create_all_indicators` using async and semaphores ([#254])
- Support choosing a single indicator and/or single layer for CLI command `create_all_indicators` ([#254])
- Indicators based on GHS-POP use raster file stored on disk instead of raster in the database ([#276])

[#221]: https://github.com/GIScience/ohsome-quality-analyst/pull/221
[#227]: https://github.com/GIScience/ohsome-quality-analyst/pull/227
[#239]: https://github.com/GIScience/ohsome-quality-analyst/pull/239
[#242]: https://github.com/GIScience/ohsome-quality-analyst/pull/242
[#245]: https://github.com/GIScience/ohsome-quality-analyst/pull/245
[#246]: https://github.com/GIScience/ohsome-quality-analyst/pull/246
[#254]: https://github.com/GIScience/ohsome-quality-analyst/pull/254
[#266]: https://github.com/GIScience/ohsome-quality-analyst/pull/266
[#276]: https://github.com/GIScience/ohsome-quality-analyst/pull/276
[`rasterstats`]: https://github.com/perrygeo/python-rasterstats
[`openpoiservice`]: https://github.com/GIScience/openpoiservice


## 0.8.0

### Breaking Changes

- Remove "IDEAL-VGI Land Use and Land Cover" as valid layer for the Mapping Saturation indicator ([#221])
- Disable support of the parameter `bpolys` for GET requests to the API ([#223])
- Rewrite of the Mapping Saturation indicator to use statistical models from the R language ([#170])

### Other Changes

- Improve API Swagger interface by adding more examples and better documentation ([#237])
- Make `pydantic` data models more modular ([#237])
- Use [`scipy`] to fit sigmoid curves to data for the Mapping Saturation indicator ([#170])

### How to upgrade

- `ideal_vgi_lulc` is not a valid layer for the Mapping Saturation indicator anymore ([#221])
- For requests to the `/indicator` or `/report` endpoints of the API for a custom AOI (usage of the `bpolys` parameter): use the POST method ([#223])
- `R` (≥ 4.0) needs to be available on the system on which OQT runs ([#170])

[#170]: https://github.com/GIScience/ohsome-quality-analyst/pull/170
[#223]: https://github.com/GIScience/ohsome-quality-analyst/pull/223
[#227]: https://github.com/GIScience/ohsome-quality-analyst/pull/227
[#237]: https://github.com/GIScience/ohsome-quality-analyst/pull/237
[`scipy`]: https://scipy.org/


## 0.7.0

### Breaking Changes

- Change API Path parameter `name` to be a Query parameter instead of a Path parameter ([#190])
- Change type of API parameter `bpolys` for POST requests to JSON (`dict`) instead of string ([#204])
- Add parameter to retrieve API response without the figure as `svg` string in the result. Default to not exclude the figure. ([#137])
- Rename `LastEdit` indicator to `Currentness` ([#178])

### Other Changes

- API: Change media type of GeoJSON response ([#199])
- Validate indicator-layer combination with `pydantic` ([#190])
- Improve API response when an error occurs by including information about the cause ([#186])
- Add parameter to get API response without svg string in the result ([#137])
- Extend time range for the `Currentness` indicator ([#178])

### How to upgrade

- Update requests for `/indicator` and `/report` endpoints. `name` is now a Query parameter. ([#190])
    - E.g. `/indicator/GhsPopComparisonBuilding` -> `indicator?name=GhsPopComparisonBuilding`
- Update `bpolys` parameter of POST requests to be a GeoJSON object instead of a string ([#204])
- To retrieve a figure for the result as `SVG` string from the `/indicator` and `/report` endpoints set the request parameter 'includeSvg' to True ([#137])
- Update requests for the indicator `Last Edit` which is now named `Currentness` ([#178])
    - E.g. `/indicator?name=Currentness`

[#137]: https://github.com/GIScience/ohsome-quality-analyst/issues/137
[#178]: https://github.com/GIScience/ohsome-quality-analyst/pull/178
[#186]: https://github.com/GIScience/ohsome-quality-analyst/pull/186
[#190]: https://github.com/GIScience/ohsome-quality-analyst/pull/190
[#199]: https://github.com/GIScience/ohsome-quality-analyst/pull/199
[#204]: https://github.com/GIScience/ohsome-quality-analyst/pull/204


## 0.6.0

### Breaking Changes

- Save indicator as GeoJSON Feature to DB ([#149])
    - Extend database schema with one additional attribute `feature` of type JSON
- API endpoint `/regions` responds with an array of names and ids (default) or a GeoJSON if parameter `asGeoJSON=True` is set ([#171], [#195])

### New Features

- Add API-endpoints to list indicators, reports, layers, datasets and feature id fields ([#106])
- Add request models, data validation and documentation to the API with the [`pydantic`] library ([#102])

### Other Changes

- Added documentation on “How to add a layer definitions” ([#141])
- Use concurrency when creating all indicators ([#153])
- Add and improve tests for API ([#168])
    - Add test cases covering the content of GeoJSON properties.
    - Improve API response schemata by using less logic to create the schemata.
- Add list indicator/layer combinations for API and CLI([#99])
- Load indicator from DB will also load its data attributes ([#179])
- Change output of CLI command `list-regions` to a pretty printed table of names and identifies ([#65], [#196])

### How to upgrade?

- If you set up your own database you will need to rebuild the database or delete the results table (`DROP TABLE results;`).
- If you used the API endpoint `/regions` be aware of the changed output format ([#171], [#195]). If you want to retrieve a GeoJSON use the parameter `asGeoJSON=True`.

[#65]: https://github.com/GIScience/ohsome-quality-analyst/issues/65
[#99]: https://github.com/GIScience/ohsome-quality-analyst/issues/99
[#102]: https://github.com/GIScience/ohsome-quality-analyst/pull/102
[#106]: https://github.com/GIScience/ohsome-quality-analyst/issues/106
[#141]: https://github.com/GIScience/ohsome-quality-analyst/pull/141
[#149]: https://github.com/GIScience/ohsome-quality-analyst/pull/149
[#153]: https://github.com/GIScience/ohsome-quality-analyst/pull/153
[#168]: https://github.com/GIScience/ohsome-quality-analyst/pull/168
[#171]: https://github.com/GIScience/ohsome-quality-analyst/issues/171
[#179]: https://github.com/GIScience/ohsome-quality-analyst/pull/179
[#195]: https://github.com/GIScience/ohsome-quality-analyst/pull/195
[#196]: https://github.com/GIScience/ohsome-quality-analyst/pull/196
[`pydantic`]: https://pydantic-docs.helpmanual.io/


## 0.5.1

- Apply breaking changes from 0.5.0 ([#100], [#130]) to the webclient ([#132])

[#132]: https://github.com/GIScience/ohsome-quality-analyst/pull/132


## 0.5.0

### Breaking Changes

- API response is a valid GeoJSON and equates to the CLI file output ([#100], [#130])
    - API output schema changes completely to a GeoJSON output
    - Indicator and report data and results are written in a flat hierarchy to the properties' field of the GeoJSON
    - Example responses can be found in the [API documentation](/docs/api.md)

### Bug Fixes

- Fix error raised by the `geojson` library while serializing JSON that includes NaN values ([#112])
- Fix error on slow mobiles where the dependencies would not be loaded correctly ([#122])
- Fix error where region selection was inconsistent on mobile ([#122])
- Fix Mapping Saturation indicator bug ([#123])
    - Added checks for NaN-values in variable inits5curves, which lead to false error-calculation.

### New Features

- FeatureCollection with multiple Features allowed as input to the API ([#100])
- Add new layer definitions for the IdealVGI project ([#134])

### Other Changes

- Set proper User Agent for requests to the ohsome API ([#62])
- Set log level matplotlib fontmanager to INFO ([#90])
- Make VCR mode configurable ([#95])
- Minor improvements to the metadata and docstrings of indicators ([#110])
- Change return type from bool to None for indicator for functions: preprocess, calculate, create_figure ([#96])
- Implement mapping of custom feature id to default (unique) feature id ([#83])
- Add osm-timestamps to indicators ([#101])
- Add timezone to oqt-timestamp ([#101])
- Update UML Component Diagram ([#136])

[#62]: https://github.com/GIScience/ohsome-quality-analyst/issues/62
[#83]: https://github.com/GIScience/ohsome-quality-analyst/pull/83
[#90]: https://github.com/GIScience/ohsome-quality-analyst/issues/90
[#95]: https://github.com/GIScience/ohsome-quality-analyst/pull/95
[#96]: https://github.com/GIScience/ohsome-quality-analyst/pull/96
[#100]: https://github.com/GIScience/ohsome-quality-analyst/pull/100
[#101]: https://github.com/GIScience/ohsome-quality-analyst/pull/101
[#110]: https://github.com/GIScience/ohsome-quality-analyst/pull/110
[#112]: https://github.com/GIScience/ohsome-quality-analyst/pull/112
[#122]: https://github.com/GIScience/ohsome-quality-analyst/pull/122
[#123]: https://github.com/GIScience/ohsome-quality-analyst/pull/123
[#130]: https://github.com/GIScience/ohsome-quality-analyst/pull/130
[#134]: https://github.com/GIScience/ohsome-quality-analyst/pull/134
[#136]: https://github.com/GIScience/ohsome-quality-analyst/pull/136


## 0.4.0

### Breaking Changes

- Change type of attribute bpolys to be GeoJSON.Feature ([#69])

### New Features

- Add option to select different datasets and fid fields as input to OQT ([#4])
- Return a GeoJSON when computing an indicator from the CLI using a dataset and FID ([#57])

### Other Changes

- Add check and custom exception for an invalid indicator layer combination during initialization of indicator objects ([#28])
- Add pre-commit check for [PEP 8] conform names by adding the pep8-naming package as development dependency ([#40])
- Raise exceptions in the ohsome client instead of returning None in case of a failed ohsome API query ([#29])
- Rewrite save and load indicator from database logic to use one result table for all indicator results ([#37])
- Remove GUF Comparison indicator ([#55])
- Implement combine_indicators() as Concrete Method of the Base Class Report ([#53])
- Small changes to the Website ([#61])
  - Change HTML parameters from countryID and topic to id and report ([#30])
  - Mention API and GitHub on About page ([#5])
  - On Click to marker now only zooms to polygon instead to fixed value 
- Update MapAction layers and POC report ([#56])
- Simplify CLI option handling by only allowing one option at a time to be added ([#54])
- Redefine OQT regions ([#26])
- Use ohsome API endpoint `/contributions/latest/count` for Last Edit indicator ([#68])
- Implement `as_feature` function for indicator and report classes ([#86])

[#4]: https://github.com/GIScience/ohsome-quality-analyst/issues/4
[#5]: https://github.com/GIScience/ohsome-quality-analyst/issues/5
[#26]: https://github.com/GIScience/ohsome-quality-analyst/issues/26
[#28]: https://github.com/GIScience/ohsome-quality-analyst/pull/28
[#29]: https://github.com/GIScience/ohsome-quality-analyst/pull/29
[#30]: https://github.com/GIScience/ohsome-quality-analyst/issues/30
[#37]: https://github.com/GIScience/ohsome-quality-analyst/pull/37
[#40]: https://github.com/GIScience/ohsome-quality-analyst/pull/40
[#53]: https://github.com/GIScience/ohsome-quality-analyst/pull/53
[#54]: https://github.com/GIScience/ohsome-quality-analyst/pull/54
[#55]: https://github.com/GIScience/ohsome-quality-analyst/pull/55
[#56]: https://github.com/GIScience/ohsome-quality-analyst/pull/56
[#57]: https://github.com/GIScience/ohsome-quality-analyst/pull/57
[#61]: https://github.com/GIScience/ohsome-quality-analyst/pull/61
[#68]: https://github.com/GIScience/ohsome-quality-analyst/pull/68
[#69]: https://github.com/GIScience/ohsome-quality-analyst/pull/69
[#86]: https://github.com/GIScience/ohsome-quality-analyst/pull/86
[PEP 8]: https://www.python.org/dev/peps/pep-0008/


## 0.3.1

### Bug Fixes

- Fix wrong layer name for Map Action Report ([#19])

[#19]: https://github.com/GIScience/ohsome-quality-analyst/pull/19


## 0.3.0

### Breaking Changes

- Database schema changes: Add timestamp to indicator results !125
- Database schema changes of the regions table !120
    - Rename attributes `infile` to `name`
    - Change geometry type from polygon to multipolygon

### New Features

- Add data input and output attributes to indicator !129
- Return a GeoJSON when computing an indicator from the CLI !140
- Retrieve available regions through API and CLI !120

### Performance and Code Quality

- Improve report tests by using mocks to avoid querying ohsome API !116
- Integrate [VCR.py](https://vcrpy.readthedocs.io) to cache data for tests !133
- Database can be setup with available regions for development or with only regions for testing !120

### Other Changes

- Different validation processes of input geometry for entry points (API and CLI) !119
- Add review process description to contributing guidelines !124
- Improve documentation !128 !144 !150
- Add license: GNU AGPLv3 !134
- Update dependencies !139
- Tidy up repository !138 !120
- Changes to available regions for pre-computed results !120:
    - Remove fid attribute from GeoJSON Feature object properties and add id attribute to GeoJSON Feature object
    - Rename test_regions to regions
    - Extent regions with four countries (#196)
    - Correct geometry of following duplicated regions: id 2 and id 28
    - Remove and download regions.geojson instead
    - Website will use regions.geojson when present. Otherwise, it will use the API endpoint.


## 0.2.0

- Refine `pyproject.toml` !65
- Minor improvements of the documentation !67
- Update pre-commit to not make changes !69
- Rename uvicorn runner script and integrate it into Docker setup !70
- Improve error handling of database authentication module !72
- Add force recreate indicator/report option !75
- Minor changes to the code structure !77 !79 !83 !90 !93
- ohsome API requests are performed asynchronously !80
- Use official Python Dockerfile as base Dockerfile for OQT !81
- Improve docs structure !91
- Bug fixes !92
- Improve logging messages #146
- Implement new indicator tag_ratio !85
- Remove psycopg2-binary and auth.py in favor of asyncpg and client.py !93
- Remove database and feature_id attributes from indicator classes !93
- Implement async/await for geodatabase !93
- Update dependencies #109
- Change API response to avoid overriding indicators !108 #203
- Put JRC Report on website !107 #189


## 0.1.0

- Change description for Mapping Saturation indicator !63
- Add undefined label to GHS_POP !55
- Add uvicorn runner for development setup !54
- Improve logging !54
- Update to poetry 1.0 and update dependencies !51
- Fixes `Last Edit` indicator in cases where it can not be calculated !50
- Fix handling of NaN value errors in mapping saturation indicator !48
- Fix response to be initialized for every request !47
- Improve docs on development setup and testing !45
- Force the recreation of all indicator through CLI !38
- Development setup of database using Docker !33 !37
- Separate integration tests from unit tests #116
- Add contribution information on issues, merge requests and changelog !31


## 0.1.0-rc1

- Review docs on all parts of OQT - if they are existent/complete/understandable #71
- GhsPopComparison: Raster and geometry do not have the same SRID #86
- Short and precise documentation on how to set up and how to contribute #46
- Define API response format #16
- Unresolved merge conflict lines on the about page #82
- Wrong filename for figures #78
- Store svg string in database and not filepath #79
- Clean up API endpoints #51
- Wrong ohsome API endpoint in last edit indicator #77
- Errors during creation of the mapping saturation indicator for test_regions #72
- Specify where metadata about an indicator should be stored #25
- Indicator class should have a result, and a metadata attribute #53
- Finish work on saturation indicator #50
- Move ohsome API related code and definitions to own module #52
- Decide on a Project Name #35
- Document what is currently working, what is still missing #49
