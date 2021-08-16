# API

## Response Examples

Indicator:

```txt
{
  "apiVersion": "0.4.0",
  "attribution": {
    "text": "© OpenStreetMap contributors",
    "url": "https://ohsome.org/copyrights"
  },
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [...]
  },
  "properties": {
    "metadata.name": "GHS-POP Comparison Buildings",
    "metadata.description": "..."
    "layer.name": "Building Count",
    "layer.description": "..."
    "result.timestamp_oqt": "..."
    "result.timestamp_osm": "...",
    "result.label": "green",
    "result.value": 1,
    "result.description": "...",
    "result.svg": "..."
    "result.data": "...",
    "data.pop_count": "...",
    "data.area": "...",
    "data.pop_count_per_sqkm": "...",
    "data.feature_count": "...",
    "data.feature_count_per_sqkm": "..."
  }
}
```


Report:

```txt
{
  "apiVersion": "0.4.0",
  "attribution": {
    "text": "© OpenStreetMap contributors",
    "url": "https://ohsome.org/copyrights"
  },
  "type": "Feature",
  "geometry": {
    "type": "MultiPolygon",
    "coordinates": [...]
  },
  "properties": {
    "report.metadata.name": "Simple Report",
    "report.metadata.description": "...",
    "report.result.label": "yellow",
    "report.result.value": 0.75,
    "report.result.description": "...",
    "indicators.0.metadata.name": "Mapping Saturation",
    "indicators.0.metadata.description": "...",
    "indicators.0.layer.name": "Building Count",
    "indicators.0.layer.description": "...",
    "indicators.0.result.timestamp_oqt": "...",
    "indicators.0.result.timestamp_osm": "...",
    "indicators.0.result.label": "yellow",
    "indicators.0.result.value": 0.5,
    "indicators.0.result.description": "..."
    "indicators.0.result.svg": "..."
    "indicators.0.result.data": "...",
    "indicators.0.data.time_range": "...",
    "indicators.0.data.saturation": "...",
    "indicators.0.data.growth": "...",
    "indicators.0.data.preprocessing_results": "...",
    "indicators.1.metadata.name": "GHS-POP Comparison Buildings",
    "indicators.1.metadata.description": "...",
    "indicators.1.layer.name": "Building Count",
    "indicators.1.layer.description": "...",
    "indicators.1.result.timestamp_oqt": "...",
    "indicators.1.result.timestamp_osm": "...",
    "indicators.1.result.label": "green",
    "indicators.1.result.value": 1,
    "indicators.1.result.description": "...",
    "indicators.1.result.svg": "..."
    "indicators.1.result.data": "...",
    "indicators.1.data.pop_count": "...",
    "indicators.1.data.area": "...",
    "indicators.1.data.pop_count_per_sqkm": "...",
    "indicators.1.data.feature_count": "...",
    "indicators.1.data.feature_count_per_sqkm": "..."
  }
}
```
