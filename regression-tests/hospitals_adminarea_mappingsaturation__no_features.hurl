POST {{BASE_URL}}/indicators/mapping-saturation
accept: application/json
[Options]
verbose: true
file,hospitals_adminarea.json;

HTTP *

[Asserts]
duration < 20000
status == 200
bytes count > 1600

jsonpath "$.result[0].topic.name" == "Hospitals"
jsonpath "$.result[0].result.description" == "No features were mapped in this region."
jsonpath "$.result[0].result.figure.data[0].labels[0]" == "The creation of the Indicator was unsuccessful."


