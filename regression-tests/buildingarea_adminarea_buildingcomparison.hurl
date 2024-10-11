POST {{BASE_URL}}/indicators/building-comparison


accept: application/json
[Options]
verbose: true
file,buildingarea_adminarea.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 2400

jsonpath "$.result[0].topic.name" == "Building Area"
jsonpath "$.result[0].result.description" contains "The completeness of OSM buildings in your area-of-interest is high. The completeness in comparison to EUBUCCO is 104.27%. The completeness in comparison to Microsoft Building Footprints is 96.16%."
jsonpath "$.result[0].result.description" matches /^The completeness of OSM buildings in your area-of-interest is high. The completeness in comparison to EUBUCCO is 104.\d{2}%. The completeness in comparison to Microsoft Building Footprints is 96.\d{2}%.$/
jsonpath "$.result[0].result.label" == "green"





