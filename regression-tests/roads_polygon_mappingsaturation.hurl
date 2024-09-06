POST https://api.quality.ohsome.org/v1-test/indicators/mapping-saturation
accept: application/json
[Options]
verbose: true
file,roads_polygon.json;

HTTP *

[Asserts]
duration < 20000
status == 200
header "content-length" contains "24"

jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "The saturation of the last 3 years is 98.3%.High saturation has been reached (97% < Saturation ≤ 100%)."
jsonpath "$.result[0].result.figure.data[0].line.color" == "#2185D0"
jsonpath "$.result[0].result.label" == "green"





