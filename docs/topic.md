# Topic

A topic describes the request which should be made to the 
[ohsome API](https://api.ohsome.org). Each topic is representative of a 
specific set of features, aggregated information or user statistics derived from the 
OpenStreetMap database. Each topic is defined by the ohsome API `endpoint` and 
parameters for the `filter`. In addition, each topic definition has a key, name and 
description. Topic definitions are written down as YAML file at 
`workers/ohsome_quality_analyst/topics/presets.yaml`

Example:

```yaml
building_count:
  name: Building Count
  description: >-
    All buildings as defined by all objects tagged with 'building=*'.
  endpoint: elements/count
  filter: building=* and geometry:polygon
```


## How to add a new topic?

First create an ohsome API query to retrieve desired information from the ohsome API. 
Helpful resources for this task are:
- Interactive ohsome API interface: https://api.ohsome.org/v1/swagger-ui.html
- ohsome API documentation on the `endpoint`s: 
  https://docs.ohsome.org/ohsome-api/stable/endpoints.html
- ohsome API documentation on the `filter` parameter: 
  https://docs.ohsome.org/ohsome-api/stable/filter.html

Second translate the query parameters into a topic definition and extent the file 
`workers/ohsome_quality_analyst/topics/presets.yaml`.

Thirdly specify for which indicator class this topic definition is a valid input. Add 
those indicator/topic combinations to the `INDICATOR_TOPIC` tuple in the 
`workers/ohsome_quality_analyst/utils/definitions.py` module. The tuple consists of the 
indicator class name and the topic definitions key as strings (E.g. 
`("MappingSaturation", "building_count")`). If the specification was 
successfully added to the tuple it is shown in the return of the command 
`oqt list-topics`.

At last run `oqt create-indicator --topic-key new-topic [...]` to check if the new topic can be used to make requests to the ohsome API and create an indicator successfully.
