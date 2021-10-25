from urllib.parse import urlencode

import requests

# Example 1
# Note the question mark (`?`) marking the start of a query string.
url = "https://oqt.ohsome.org/api/indicator?"
parameters = {
    "name": "GhsPopComparisonBuildings",
    "layerName": "building_count",
    "dataset": "regions",
    "featureId": "3",
}
# Use `urllib.parse.urlencode` to ensure proper URL encoding:
response = requests.get(url + urlencode(parameters))
assert response.status_code == 200

# Example 2
# Note the *missing* question mark (`?`).
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
# Note the using of the `json` library to dump the GeoJSON as string to the parameters.
# URL encoding will be done by the requests library.
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
