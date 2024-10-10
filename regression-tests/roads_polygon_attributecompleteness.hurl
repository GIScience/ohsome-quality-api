POST {{BASE_URL}}/indicators/attribute-completeness
accept: application/json
[Options]
verbose: true
file,roads_polygon_maxspeed.json;

HTTP *

[Asserts]
duration < 5000
status == 200
bytes count > 1900

jsonpath "$.result[0].metadata.name" == "Attribute Completeness"
jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "The ratio of the features (all: 1034408.4) compared to features with expected tags (matched: 278118.2) is 0.27. Around 25-75% of the features match the expected tags."
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "yellow"




