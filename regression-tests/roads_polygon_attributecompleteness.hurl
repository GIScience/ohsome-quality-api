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
jsonpath "$.result[0].result.description" matches /^26\.\d{1}% of all "roads" features \(all: 103\d{1}\.\d{2} km\) in your area of interest have the selected additional attribute maxspeed \(matched: 27\d{1}\.\d{2} km\)\. The attribute completeness is medium \(25%-75%\)\.$/
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "yellow"




