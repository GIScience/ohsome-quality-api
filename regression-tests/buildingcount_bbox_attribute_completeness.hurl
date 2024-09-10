POST https://api.quality.ohsome.org/v1-test/indicators/attribute-completeness
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
jsonpath "$.result[0].result.description" contains "The ratio of the features (all: 67.0) compared to features with expected tags (matched: 57.0) is 0.85."
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "green"




