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
        "ratio_filter"): str,
    },
    "result": {
        "timestamp_oqt": str,
        "timestamp_osm": str,
        "value": float,
        "label": str,
        "description": str,
        "svg": str,
        "data": { ... }
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
                "ratio_filter": str,
            },
            "result": {
                "timestamp_oqt": str,
                "timestamp_osm": str,
                "value": float,
                "label": str,
                "description": str,
                "svg": str,
                "data": { ... },
            },
        }
    },
}
```
