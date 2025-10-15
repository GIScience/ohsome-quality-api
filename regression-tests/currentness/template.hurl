POST $base_url/indicators/$indicator
accept: application/json
{
    "topic": "$topic",
    "ohsomedb": "$ohsomedb",
    "bpolys": $bpolys
}
HTTP 200
[Captures]
duration_in_ms: duration
