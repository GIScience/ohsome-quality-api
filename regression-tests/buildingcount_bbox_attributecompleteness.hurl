POST {{BASE_URL}}/indicators/attribute-completeness
accept: application/json
[Options]
verbose: true
file,buildingcount_bbox_housenumber.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 1700

jsonpath "$.result[0].metadata.name" == "Attribute Completeness"
jsonpath "$.result[0].topic.name" == "Building Count"
jsonpath "$.result[0].result.description" matches /^85\.\d{1}% of all "building count" features \(all: 6\d{1} elements\) in your area of interest have the selected additional attribute house number address \(matched: 5\d{1} elements\)\. The attribute completeness is high \(>75%\)\.$/
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "green"




