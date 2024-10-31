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
jsonpath "$.result[0].result.description" matches /^The ratio of the features \(all: 103\d{4}\.\d{1}\) compared to features with expected tags \(matched: 278\d{3}\.\d{1}\) is 0\.2\d{1}\. Around 25-75% of the features match the expected tags\.$/
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "yellow"




