POST https://api.quality.ohsome.org/v1-test/indicators/road-comparison
accept: application/json
[Options]
verbose: true
file,roads_adminarea.json;

HTTP *

[Asserts]
duration < 20000
status == 200
header "content-length" contains "22"

jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "Microsoft Roads has a road length of 31.94 km, of which 31.82 km are covered by roads in OSM. The completeness of OSM roads in your area-of-interest is high."
jsonpath "$.result[0].result.label" == "green"





