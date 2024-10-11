POST {{BASE_URL}}/indicators/mapping-saturation
accept: application/json
[Options]
verbose: true
file,roads_polygon.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 24000

jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "The saturation of the last 3 years is 98.46%.High saturation has been reached (97% < Saturation ≤ 100%)."
jsonpath "$.result[0].result.description" contains "The saturation of the last 3 years is 98"
jsonpath "$.result[0].result.description" contains ".High saturation has been reached (97% < Saturation ≤ 100%)."
jsonpath "$.result[0].result.figure.data[0].line.color" == "#2185D0"
jsonpath "$.result[0].result.label" == "green"





