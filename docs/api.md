# API

## Response Examples

### Indicator

```txt
{
  "apiVersion": "0.6.0",
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
    "metadata.description": "Comparison between population density and feature density.\nThis can give an estimate if mapping has been completed.\n",
    "layer.name": "Building Count",
    "layer.description": "All buildings as defined by all objects tagged with 'building=*'.\n",
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


### Report

```txt
{
  "apiVersion": "0.6.0",
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
    "report.metadata.name": "Simple Report",
    "report.metadata.description": "This report shows the quality for two indicators:\nmapping-saturation and ghspop-comparison.\nIt's main function is to test the interactions between\ndatabase, api and website.\n",
    "report.result.label": "yellow",
    "report.result.value": 0.75,
    "report.result.description": "At least one indicator shows only medium quality.\nYou should inspect the results for the individual indicators\nto identify potential data quality concerns.\n",
    "indicators.0.metadata.name": "Mapping Saturation",
    "indicators.0.metadata.description": "Calculate if mapping has saturated.\n",
    "indicators.0.layer.name": "Building Count",
    "indicators.0.layer.description": "All buildings as defined by all objects tagged with 'building=*'.\n",
    "indicators.0.result.timestamp_oqt": "2021-10-05T09:33:30.851900+00:00",
    "indicators.0.result.timestamp_osm": "2021-09-01T00:00:00+00:00",
    "indicators.0.result.label": "yellow",
    "indicators.0.result.value": 0.5,
    "indicators.0.result.description": "...",
    "indicators.0.result.svg": "...",
    "indicators.0.data.time_range": "2008-01-01//P1M",
    "indicators.0.data.values": [ ... ],
    "indicators.0.data.values_normalized": [ ... ]
    "indicators.0.data.timestamps": [ ... ]
    "indicators.0.data.no_data": false,
    "indicators.0.data.deleted_data": false,
    "indicators.0.data.saturation": 0.9575133534830439,
    "indicators.0.data.growth": 0.042486646516956106,
    "indicators.1.metadata.name": "GHS-POP Comparison Buildings",
    "indicators.1.metadata.description": "Comparison between population density and feature density.\nThis can give an estimate if mapping has been completed.\n",
    "indicators.1.layer.name": "Building Count",
    "indicators.1.layer.description": "All buildings as defined by all objects tagged with 'building=*'.\n",
    "indicators.1.result.timestamp_oqt": "2021-10-05T09:33:30.671060+00:00",
    "indicators.1.result.timestamp_osm": "2021-09-26T20:00:00+00:00",
    "indicators.1.result.label": "green",
    "indicators.1.result.value": 1,
    "indicators.1.result.description": "...",
    "indicators.1.result.svg": "...",
    "indicators.1.data.pop_count": 533351.7174390131,
    "indicators.1.data.area": 70.29342423663759,
    "indicators.1.data.pop_count_per_sqkm": 7587.5051362347085,
    "indicators.1.data.feature_count": 69993,
    "indicators.1.data.feature_count_per_sqkm": 995.7261402485354
  }
}
```
