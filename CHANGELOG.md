# Changelog

## Current Main

- Add check and custom exception for an invalid indicator layer combination during initialization of indicator objects ([#28])
- Add pre-commit check for [PEP 8] conform names by adding the pep8-naming package as development dependency ([#40])
- Raise exceptions in the ohsome client instead of returning None in case of a failed ohsome API query ([#29])
- Add option to select different datasets and fid fields as input to OQT ([#4])
- Rewrite save and load indicator from database logic to use one result table for all indicator results ([#37])
- Remove GUF Comparison indicator ([#55])
- Implement combine_indicators() as Concrete Method of the Base Class Report ([#53])
- Small changes to the Website ([#61])
  - Change HTML parameters from countryID and topic to id and report ([#30])
  - Mention API and GitHub on About page ([#5])
  - On Click to marker now only zooms to polygon instead to fixed value 
- Return a GeoJSON when computing an indicator from the CLI using a dataset and FID ([#57])
- Update MapAction layers and POC report ([#56])
- Simplify CLI option handling by only allowing one option at a time to be added ([#54])
- Redefine OQT regions ([#26])
- Use ohsome API endpoint `/contributions/latest/count` for Last Edit indicator ([#68])
- Change type of attribute bpolys to be of Polygon or MultyPolygon ([63])

[#28]: https://github.com/GIScience/ohsome-quality-analyst/pull/28
[#40]: https://github.com/GIScience/ohsome-quality-analyst/pull/40
[PEP 8]: https://www.python.org/dev/peps/pep-0008/
[#29]: https://github.com/GIScience/ohsome-quality-analyst/pull/29
[#4]: https://github.com/GIScience/ohsome-quality-analyst/issues/4
[#37]: https://github.com/GIScience/ohsome-quality-analyst/pull/37
[#55]: https://github.com/GIScience/ohsome-quality-analyst/pull/55
[#53]: https://github.com/GIScience/ohsome-quality-analyst/pull/53
[#30]: https://github.com/GIScience/ohsome-quality-analyst/issues/30
[#5]: https://github.com/GIScience/ohsome-quality-analyst/issues/5
[#61]: https://github.com/GIScience/ohsome-quality-analyst/pull/61
[#57]: https://github.com/GIScience/ohsome-quality-analyst/pull/57
[#56]: https://github.com/GIScience/ohsome-quality-analyst/pull/56
[#54]: https://github.com/GIScience/ohsome-quality-analyst/pull/54
[#26]: https://github.com/GIScience/ohsome-quality-analyst/issues/26
[#68]: https://github.com/GIScience/ohsome-quality-analyst/pull/68
[#63]: https://github.com/GIScience/ohsome-quality-analyst/pull/63


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
- Force recreate all indicator through CLI !38
- Development setup of database using Docker !33 !37
- Separate integration tests from unit tests #116
- Add contribution information on issues, merge requests and changelog !31


## 0.1.0-rc1

- Review docs on all parts of OQT - if they are existent/complete/understandable #71
- GhsPopComparison: Raster and geometry do not have the same SRID #86
- Short and precise documentation on how to setup and how to contribute #46
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
