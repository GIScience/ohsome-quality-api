GET {{BASE_URL}}/metadata?project=all
accept: application/json
[Options]
verbose: true

HTTP *

[Asserts]
duration < 2000
status == 200
bytes count > 25000

jsonpath "$.result.indicators.mapping-saturation.description" contains "Calculate if mapping has saturated."
jsonpath "$.result.indicators.currentness.description" contains "Estimate currentness of features"
jsonpath "$.result.topics.building-count.aggregationType" == "count"
jsonpath "$.result.topics.roads.aggregationType" == "length"
jsonpath "$.result.qualityDimensions.minimal.name" == "Minimal"
jsonpath "$.result.projects.core.description" == "something that is still a TODO"
