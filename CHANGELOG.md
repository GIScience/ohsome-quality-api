# Changelog

## 0.3.0

- Different validation processes of input geometry for entry points (API and CLI) !119
- Add review process description to contributing guidelines !124
- Improve report tests by using mocks to avoid querying ohsome API !116
- Improve documentation !128
- Add license: GNU AGPLv3 !134
- Add data input and output attributes to indicator !129
- Update dependecies !139

## 0.2.0

- Refine `pyproject.toml` !65
- Minor improvements of the documentation !67
- Update pre-commit to not make changes !69
- Rename uvicorn runner script and integrate it into Docker setup !70
- Improve error handling of database authetication module !72
- Add force recreate indicator/report option !75
- Minor changes to the code structure !77 !79 !83 !90 !93
- ohsome API requests are performed asynchronously !80
- Use offical Python Dockerfile as base Dockerfile for OQT !81
- Improve docs structure !91
- Bug fixes !92
- Improve logging messages #146
- Implement new indicator tag_ratio !85
- Remove psycopg2-binary and auth.py in favor of asyncpg and client.py !93
- Remove database and feature_id attributes from indicator classes !93
- Implement async/await for geodatabase !93
- Update dependecies #109
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
