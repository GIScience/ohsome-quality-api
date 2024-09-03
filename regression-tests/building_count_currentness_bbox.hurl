POST https://api.quality.ohsome.org/v1-test/indicators/currentness
accept: application/json
[Options]
verbose: true
file,building_count_currentness.payload.json;

HTTP *

[Asserts]
duration < 20000
status == 200
header "content-length" contains "20"

jsonpath "$.result[0].topic.name" == "Building Count"
jsonpath "$.result[0].result.description" contains "In the area of interest 16% of the 67 features were edited"
jsonpath "$.result[0].result.figure.data[1].marker.color" == "#21BA45"
jsonpath "$.result[0].result.label" == "red"




