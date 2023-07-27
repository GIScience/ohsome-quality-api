# Topic

A topic describes the request which should be made to the [ohsome API](https://api.ohsome.org). Each topic is representative of a specific set of features, aggregated information or user statistics derived from the OpenStreetMap database. Each topic is defined by the ohsome API `endpoint`, an `aggregation_type` and the `filter` parameter. In addition, each topic preset has a key, name, description, a list of valid indicators and a list of projects the topic belongs to. Topic presets are written down as YAML file at `ohsome_quality_analyst/topics/presets.yaml`

## Example

```yaml
building-count:
  name: Building Count
  description: >-
    All buildings as defined by all objects tagged with 'building=*'.
  endpoint: elements
  aggregation_type: count
  filter: building=* and geometry:polygon
  indicators:
    - mapping-saturation
    - currentness
    - attribute-completeness
  projects:
    - core
```

## How to Add a New Topic?

First create an ohsome API query to retrieve desired information from the ohsome API. Helpful resources for this task are:
- The Swagger UI of the ohsome API:
  https://api.ohsome.org/v1/swagger-ui.html
- ohsome API documentation on the `aggregation_type` and `endpoint` parameters: 
  https://docs.ohsome.org/ohsome-api/stable/endpoints.html
- ohsome API documentation on the `filter` parameter:
  https://docs.ohsome.org/ohsome-api/stable/filter.html

Second translate the query parameters into a topic preset and extent this file:
`ohsome_quality_analyst/topics/presets.yaml`.
