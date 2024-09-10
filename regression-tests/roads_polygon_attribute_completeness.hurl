POST https://api.quality.ohsome.org/v1-test/indicators/attribute-completeness
accept: application/json
[Options]
verbose: true
file,roads_polygon_attribute_completeness_maxspeed.json;

HTTP *

[Asserts]
duration < 5000
status == 200
bytes count > 1900

jsonpath "$.result[0].metadata.name" == "Attribute Completeness"
jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "The ratio of the features (all: 1034299.9) compared to features with expected tags (matched: 276785.2) is 0.27."
jsonpath "$.result[0].result.figure.data[0].gauge.steps[0].color" == "tomato"
jsonpath "$.result[0].result.label" == "yellow"




