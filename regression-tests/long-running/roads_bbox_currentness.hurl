POST {{base_url}}/indicators/currentness
accept: application/json
[Options]
verbose: true
file,roads_bbox.json;

HTTP *

[Asserts]
duration < 300000
status == 200
bytes count > 20000

jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "Please note that in the area of interest less than 25 features of the selected topic are present today."
jsonpath "$.result[0].result.figure.data[1].marker.color" == "#21BA45"
jsonpath "$.result[0].result.label" == "green"




