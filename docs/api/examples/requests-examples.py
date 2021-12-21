import requests

# Example 1
url = "https://oqt.ohsome.org/api/indicator"
parameters = {
    "name": "GhsPopComparisonBuildings",
    "layerName": "building_count",
    "dataset": "regions",
    "featureId": "3",
}
response = requests.get(url, params=parameters)
assert response.status_code == 200

# Example 2
url = "https://oqt.ohsome.org/api/indicator"
parameters = {
    "name": "GhsPopComparisonBuildings",
    "layerName": "building_count",
    "dataset": "regions",
    "featureId": "3",
}
response = requests.post(url, json=parameters)
assert response.status_code == 200

# Example 3
url = "https://oqt.ohsome.org/api/indicator"
bpolys = {
    "type": "Polygon",
    "coordinates": [
        [
            [8.674092292785645, 49.40427147224242],
            [8.695850372314453, 49.40427147224242],
            [8.695850372314453, 49.415552187316095],
            [8.674092292785645, 49.415552187316095],
            [8.674092292785645, 49.40427147224242],
        ]
    ],
}
parameters = {
    "name": "GhsPopComparisonBuildings",
    "layerName": "building_count",
    "bpolys": bpolys,
}
response = requests.post(url, json=parameters)
assert response.status_code == 200
