curl --request GET "https://oqt.ohsome.org/api/indicator?name=GhsPopComparisonBuildings&layerName=building_count&dataset=regions&featureId=3"

curl --request POST \
    --header "Content-Type: application/json" \
    --data '{"name": "GhsPopComparisonBuildings", "layerName": "building_count", "dataset": "regions", "featureId": 3}' \
    "https://oqt.ohsome.org/api/indicator"

curl --request POST \
    --header "Content-Type: application/json" \
    --data @data.json \
    "https://oqt.ohsome.org/api/indicator"
