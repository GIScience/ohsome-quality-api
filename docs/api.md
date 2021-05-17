# API

## Response Schema

Indicator:

```json
{
    "attribution": {
        "url": str,
        "text": str,
    },
    "apiVersion": str,
    "metadata": {
        "name": str,
        "requestUrl": str,
        "description": str,
    },
    "layer": {
        "name": str,
        "description": str,
        "endpoint": str,
        "filter": str,
        Optional("ratio_filter"): Or(str, None),
    },
    "result": {
        "timestamp_oqt": str,
        "timestamp_osm": Or(str, None),
        "value": Or(float, None),
        "label": str,
        "description": str,
        "svg": str,
        Optional("data"): Or(dict, None),
    },
}
```


Report:

```json
{
    "attribution": {
        "url": str,
        "text": str,
    },
    "apiVersion": str,
    "metadata": {
        "name": str,
        "description": str,
        "requestUrl": str,
    },
    "result": {
        "value": float,
        "label": str,
        "description": str,
    },
    "indicators": {
        str: {
            "metadata": {
                "name": str,
                "description": str,
            },
            "layer": {
                "name": str,
                "description": str,
                "endpoint": str,
                "filter": str,
                Optional("ratio_filter"): Or(str, None),
            },
            "result": {
                "timestamp_oqt": str,
                "timestamp_osm": Or(str, None),
                "value": Or(float, None),
                "label": str,
                "description": str,
                "svg": str,
                Optional("data"): Or(dict, None),
            },
        }
    },
}
```
