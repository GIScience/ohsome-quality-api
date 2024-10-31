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
jsonpath "$.result[0].result.description" matches /^The ratio of the features \(all: 6\d{1}\.0\) compared to features with expected tags \(matched: 5\d{1}\.0\) is 0\.8\d{1}\. More than 75% of the features match the expected tags\.$/
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "green"




