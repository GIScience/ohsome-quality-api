# API

Please have a look at the request examples of the [interactive Swagger UI](https://oqt.ohsome.org/api/docs).
Using the Swagger UI one can create valid `cURL` requests with using an interactive interface.


## Indicator Endpoint

Three types of requests can be made:

- To request an Indicator for an AOI defined by OQT provide the following parameters: `name`, `topic`, `dataset` and `featureId`
- To request an Indicator for a custom AOI provide the following parameters: parameters: `name`, `topic` and `bpolys`
- To request an Indicator for a custom AOI and custom data provide the following parameters: `name`, `bpolys` and `topic`

Depending on the input, the output will be a GeoJSON Feature or FeatureCollection with the results of the Indicator as properties. The Feature properties of the input GeoJSON will be preserved if they do not collide with the properties set by OQT.

### Parameters

| Parameter     | Description                                                                                                                                       |
| ---           | ---                                                                                                                                               |
| `name`        | Name of the indicator                                                                                                                             |
| `topic`       | Name of the topic                                                                                                                                 |
| `dataset`     | Name of the dataset containing bounding polygons                                                                                                  |
| `featureId`   | Identifier of the feature in the dataset                                                                                                          |
| `bpolys`      | Bounding polygon(s) as GeoJSON Feature, FeatureCollection, Polygon or MultiPolygon object. The Geometry has to be of type Polygon or MultiPolygon |
| `topic`       | Name, description and data of a custom topic. Data has to be provided in the same format as the response of the ohsome API would look like        |
| `includeSvg`  | Include a SVG string of a figure displaying the Indicator results                                                                                 |
| `includeHtml` | Include a HTML string with the Indicator results                                                                                                  |
| `flatten`     | Flattening of the GeoJSON properties                                                                                                              |

Parameters are in part mutual exclusive (e.g. either `dataset` and `featureId` or `bpolys`). If the response contains multiple errors probably not all required parameters and/or mutual exclusive parameters have been provided.

### A Note on the Difference of `GET` and `POST` Requests

A request can be made to the `/indicator` endpoint using either the `GET` or `POST` method. For `GET` requests to this endpoint, only the parameters `dataset` and `feature_id` are supported. This means that it is not possible to create an indicator for a custom AOI using the `bpolys` parameter by making a `GET` request to the API.

Using the `POST` method all types of requests (see above) and parameters are supported.

### Request an Indicator for an OQT AOI using Python and `requests` Library

```python
import requests

url = "https://oqt.ohsome.org/api/indicator"
parameters = {
    "name": "mapping-saturation",
    "topic": "building_count",
    "dataset": "regions",
    "featureId": 3,
    "fidField": "ogc_fid",  # Optional
    "includeSvg": False,  # Optional
    "includeHtml": False,  # Optional
    "flatten": False,  # Optional
}
# Response using the GET method
response = requests.get(url, params=parameters)
# Response using the POST method
response = requests.post(url, json=parameters)
```

### Request an Indicator for a custom AOI using Python and `requests` Library

```python
import requests

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
    "name": "mapping-saturation",
    "topic": "building_count",
    "bpolys": bpolys,
    "includeSvg": False,  # Optional
    "includeHtml": False,  # Optional
    "flatten": False,  # Optional
}
response = requests.post(url, json=parameters)
```

### Request an Indicator for a custom AOI and Topic using Python and `requests` Library

The data attached to a custom topic has to be in the same structure as the ohsome API response: [https://docs.ohsome.org/ohsome-api/stable](https://docs.ohsome.org/ohsome-api/stable)

Data used in this example has been taken from the ohsome API response of following request URL: [https://api.ohsome.org/v1/elements/count?bboxes=8.67%2C49.39%2C8.71%2C49.42&filter=building%3D\*%20and%20geometry%3Apolygon&format=json&time=2014-01-01%2F2017-01-01%2FP1M](https://api.ohsome.org/v1/elements/count?bboxes=8.67%2C49.39%2C8.71%2C49.42&filter=building%3D*%20and%20geometry%3Apolygon&format=json&time=2014-01-01%2F2017-01-01%2FP1M)

```python
import requests

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
topic = {
    "key": "my-topic-key",
    "name": "My topic name",
    "description": "My topic description",
    "data": {
        "result": [
            {"timestamp": "2014-01-01T00:00:00Z", "value": 4708},
            {"timestamp": "2014-02-01T00:00:00Z", "value": 4842},
            {"timestamp": "2014-03-01T00:00:00Z", "value": 4840},
            {"timestamp": "2014-04-01T00:00:00Z", "value": 4941},
            {"timestamp": "2014-05-01T00:00:00Z", "value": 4987},
            {"timestamp": "2014-06-01T00:00:00Z", "value": 5007},
            {"timestamp": "2014-07-01T00:00:00Z", "value": 5020},
            {"timestamp": "2014-08-01T00:00:00Z", "value": 5168},
            {"timestamp": "2014-09-01T00:00:00Z", "value": 5355},
            {"timestamp": "2014-10-01T00:00:00Z", "value": 5394},
            {"timestamp": "2014-11-01T00:00:00Z", "value": 5449},
            {"timestamp": "2014-12-01T00:00:00Z", "value": 5470},
            {"timestamp": "2015-01-01T00:00:00Z", "value": 5475},
            {"timestamp": "2015-02-01T00:00:00Z", "value": 5477},
            {"timestamp": "2015-03-01T00:00:00Z", "value": 5481},
            {"timestamp": "2015-04-01T00:00:00Z", "value": 5495},
            {"timestamp": "2015-05-01T00:00:00Z", "value": 5516},
            {"timestamp": "2015-06-01T00:00:00Z", "value": 5517},
            {"timestamp": "2015-07-01T00:00:00Z", "value": 5519},
            {"timestamp": "2015-08-01T00:00:00Z", "value": 5525},
            {"timestamp": "2015-09-01T00:00:00Z", "value": 5560},
            {"timestamp": "2015-10-01T00:00:00Z", "value": 5564},
            {"timestamp": "2015-11-01T00:00:00Z", "value": 5568},
            {"timestamp": "2015-12-01T00:00:00Z", "value": 5627},
            {"timestamp": "2016-01-01T00:00:00Z", "value": 5643},
            {"timestamp": "2016-02-01T00:00:00Z", "value": 5680},
            {"timestamp": "2016-03-01T00:00:00Z", "value": 5681},
            {"timestamp": "2016-04-01T00:00:00Z", "value": 5828},
            {"timestamp": "2016-05-01T00:00:00Z", "value": 5974},
            {"timestamp": "2016-06-01T00:00:00Z", "value": 5990},
            {"timestamp": "2016-07-01T00:00:00Z", "value": 5991},
            {"timestamp": "2016-08-01T00:00:00Z", "value": 5997},
            {"timestamp": "2016-09-01T00:00:00Z", "value": 6002},
            {"timestamp": "2016-10-01T00:00:00Z", "value": 6010},
            {"timestamp": "2016-11-01T00:00:00Z", "value": 6010},
            {"timestamp": "2016-12-01T00:00:00Z", "value": 6016},
            {"timestamp": "2017-01-01T00:00:00Z", "value": 6015},
        ]
    }
}
parameters = {
    "name": "MappingSaturation",
    "bpolys": bpolys,
    "topic": topic,
    "includeSvg": False,  # Optional
    "includeHtml": False,  # Optional
    "flatten": True,  # Optional
}
response = requests.post(url, json=parameters)
```

### Response Examples

```json
{
  "apiVersion": "0.7.0",
  "attribution": {
    "text": "© OpenStreetMap contributors",
    "url": "https://ohsome.org/copyrights"
  },
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [ ... ]
  },
  "properties": {
    "metadata.name": "GHS-POP Comparison Buildings",
    "metadata.description": "Comparison between population density and feature density. This can give an estimate if mapping has been completed. ",
    "topic.name": "Building Count",
    "topic.description": "All buildings as defined by all objects tagged with 'building=*'. ",
    "result.timestamp_oqt": "2021-10-05T09:33:30.671060+00:00",
    "result.timestamp_osm": "2021-09-26T20:00:00+00:00",
    "result.label": "green",
    "result.value": 1,
    "result.description": "...",
    "result.svg": "...",
    "data.pop_count": 533351.7174390131,
    "data.area": 70.29342423663759,
    "data.pop_count_per_sqkm": 7587.5051362347085,
    "data.feature_count": 69993,
    "data.feature_count_per_sqkm": 995.7261402485354
  }
}
```


## Report Endpoint

Two types of requests can be made:

- To request a Report for an AOI defined by OQT provide the following parameters: `name`, `dataset` and `featureId`
- To request a Report for a custom AOI provide the following parameters: parameters: `name` and `bpolys`

Depending on the input, the output will be a GeoJSON Feature or FeatureCollection with the results of the Report and each Indicator as properties. The Feature properties of the input GeoJSON will be preserved if they do not collide with the properties set by OQT.

### Parameters

| Parameter     | Description                                                                                                                                       |
| ---           | ---                                                                                                                                               |
| `name`        | Name of the Report                                                                                                                                |
| `dataset`     | Name of the dataset containing bounding polygons                                                                                                  |
| `featureId`   | Identifier of the feature in the dataset                                                                                                          |
| `bpolys`      | Bounding polygon(s) as GeoJSON Feature, FeatureCollection, Polygon or MultiPolygon object. The Geometry has to be of type Polygon or MultiPolygon |
| `includeSvg`  | Include a SVG string of a figure displaying the Indicator results                                                                                 |
| `includeHtml` | Include a HTML string with the Indicator results                                                                                                  |
| `flatten`     | Flattening of the GeoJSON properties                                                                                                              |

Some parameters are mutually exclusive (E.g. either `dataset` and `featureId` or `bpolys`). If the response contains multiple errors, it is likely that not all required parameters and/or mutually exclusive parameters have been provided.

### A Note on the Difference of `GET` and `POST` Requests

A request can be made to the `/report` endpoint using either the `GET` or `POST` method. For `GET` requests to this endpoint, only the `dataset` and `feature_id` parameters are supported. That means that it is not possible to create a Report for a custom AOI using the `bpolys` parameter by making a `GET` request to the API.

Using the `POST` method all types of requests (see above) and parameters are supported.

### Request an Report for an OQT AOI using Python and `requests` Library

```python
import requests

url = "https://oqt.ohsome.org/api/report"
parameters = {
    "name": "MinimalTestReport",
    "dataset": "regions",
    "featureId": 3,
    "includeSvg": False,  # Optional
    "includeHtml": False,  # Optional
    "flatten": False,  # Optional
}
# Response using the GET method
response = requests.get(url, params=parameters)
# Response using the POST method
response = requests.post(url, json=parameters)
```

### Request an Report for a custom AOI using Python and `requests` Library

```python
import requests

url = "https://oqt.ohsome.org/api/report"
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
    "name": "Minimal",
    "bpolys": bpolys,
    "includeSvg": False,  # Optional
    "includeHtml": False,  # Optional
    "includeData": False,  # Optional
    "flatten": False,  # Optional
}
response = requests.post(url, json=parameters)
```

### Response Examples

```json
{
  "apiVersion": "0.11.0",
  "attribution": {
    "url": "https://github.com/GIScience/ohsome-quality-analyst/blob/main/COPYRIGHTS.md",
    "text": "© OpenStreetMap contributors"
  },
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [ ... ]
  },
  "properties": {
    "report": {
      "metadata": {
        "name": "Minimal",
        "description": "This report shows the quality for two indicators: Mapping Saturation and Currentness. It's main function is to test the interactions between database and api. "
      },
      "result": {
        "class_": 5,
        "description": "All indicators show a good quality. The data in this regions seems to be completely mapped. "
      }
    },
    "indicators": [
      {
        "metadata": {
          "name": "Mapping Saturation",
          "description": "Calculate if mapping has saturated. High saturation has been reached if the growth of the fitted curve is minimal. "
        },
        "topic": {
          "key": "building_count",
          "name": "Building Count",
          "description": "All buildings as defined by all objects tagged with 'building=*'. "
        },
        "result": {
          "description": "The saturation of the last 3 years is 98.4%. High saturation has been reached (97% < Saturation ≤ 100%). ",
          "timestamp_oqt": "2022-09-07T20:00:24.897112+00:00",
          "timestamp_osm": "2022-08-01T00:00:00+00:00",
          "value": 0.9839766580301241,
          "label": "green",
          "class": 5
        }
      },
      {
        "metadata": {
          "name": "Currentness",
          "description": "Ratio of all contributions that have been edited since 2008 until the current day in relation with years without mapping activities in the same time range. Refers to data quality in respect to currentness. "
        },
        "topic": {
          "key": "building_count",
          "name": "Building Count",
          "description": "All buildings as defined by all objects tagged with 'building=*'. "
        },
        "result": {
          "description": "Over 50% of the 41638.0 features (Building Count) were edited in the last 4 years. This is a rather high value and indicates that the map features  are very unlike to be outdated. This refers to good data quality in  respect to currentness. ",
          "timestamp_oqt": "2022-09-07T20:00:24.897112+00:00",
          "timestamp_osm": "2022-08-28T08:00:00+00:00",
          "value": 0.8,
          "label": "green",
          "class": 5
        }
      }
    ]
  }
}
```
