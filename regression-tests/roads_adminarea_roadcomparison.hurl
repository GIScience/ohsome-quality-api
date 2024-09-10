POST {{base_url}}/indicators/road-comparison
accept: application/json
[Options]
verbose: true
file,roads_adminarea.json;

HTTP *

[Asserts]
duration < 5000
status == 200
bytes count > 2200

jsonpath "$.result[0].topic.name" == "Roads"
jsonpath "$.result[0].result.description" contains "Microsoft Roads has a road length of 31.94 km, of which 31.82 km are covered by roads in OSM. The completeness of OSM roads in your area-of-interest is high."
jsonpath "$.result[0].result.description" matches /^Microsoft Roads has a road length of 31.\d{2} km, of which 31.\d{2} km are covered by roads in OSM. The completeness of OSM roads in your area-of-interest is high.$/
jsonpath "$.result[0].result.label" == "green"





