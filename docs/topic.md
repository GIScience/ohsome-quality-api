# Topic

A topic describes the request which should be made to the [ohsome API](https://api.heigit.org/docs/?urls.primaryName=ohsome+API). Each topic is representative of a specific set of features, aggregated information or user statistics derived from the OpenStreetMap database. Each topic is defined by the an `aggregation_type` and the `filter` parameter. In addition, each topic preset has a key, name, description and a list of valid indicators. Topic presets are written down as YAML file at `ohsome_quality_api/topics/presets.yaml`

## Example

```yaml
buildings:
  name: Buildings
  description: >-
    All buildings as defined by all objects tagged with 'building=*'.
  aggregation_type: count
  filter: building=* and building!=no and geometry:polygon
  indicators:
    - mapping-saturation
    - currentness
    - building-comparison
    - attribute-completeness
    - user-activity
```

## How to Add a New Topic?

First create an ohsome API query to retrieve desired information from the ohsome API. Helpful resources for this task are:
- The Swagger UI of the ohsome API:
  https://api.heigit.org/docs/?urls.primaryName=ohsome+quality+API
- ohsome API documentation on the `filter` parameter:
  https://docs.ohsome.org/ohsome-api/v2-rc/reference/filter.html

Second translate the query parameters into a topic preset and extent this file:
`ohsome_quality_api/topics/presets.yaml`.
