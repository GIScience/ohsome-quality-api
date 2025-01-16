POST {{BASE_URL}}/indicators/currentness
accept: application/json
[Options]
verbose: true
file,buildingcount_bbox.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 20000

jsonpath "$.result[0].topic.name" == "Building Count"
jsonpath "$.result[0].result.description" matches /^In the area of interest 1\d{1}% of the 6\d{1} features were edited \(created or modified\) for the last time in the period between .. ... 20.. and .. ... 20...
   |Many features are out-of-date.$/
jsonpath "$.result[0].result.figure.data[1].marker.color" == "#21BA45"
jsonpath "$.result[0].result.label" == "red"




