POST {{BASE_URL}}/indicators/currentness
accept: application/json
[Options]
verbose: true
file,buildingcount_bbox.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 20000

jsonpath "$.result[0].topic.name" == "Building Count"
jsonpath "$.result[0].result.description" contains "In the area of interest 16% of the 67 features were edited"
jsonpath "$.result[0].result.description" matches /^In the area of interest 1\d{1}% of the 6\d{1} features were edited(created or modified) for the last time in the period between 01 Oct 2021 and 01 Oct 2024.
   |Many features are out-of-date.$/
jsonpath "$.result[0].result.figure.data[1].marker.color" == "#21BA45"
jsonpath "$.result[0].result.label" == "red"




