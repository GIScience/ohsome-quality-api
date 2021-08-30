# Layer

A layer describes the request which should be made to the 
[ohsome API](https://api.ohsome.org). Each layer is representative of a 
specific set of features, aggregated information or user statistics derived from the 
OpenStreetMap database. Each layer is defined by the ohsome API `endpoint` and 
parameters for the `filter`. In addition each layer definition has a key, name and 
description. Layer definitions are written down as YAML file at 
`workers/ohsome_quality_analyst/ohsome/layer_definitions.yaml`

Example:

```yaml
building_count:
  name: Building Count
  description: |
    All buildings as defined by all objects tagged with 'building=*'.
  endpoint: elements/count
  filter: building=* and geometry:polygon
```


## How to add a new layer?

First create an ohsome API query to retrieve desired information from the ohsome API. 
Helpful resources for this task are:
- Interactive ohsome API interface: https://api.ohsome.org/v1/swagger-ui.html
- ohsome API documentation on the `endpoint`s: 
  https://docs.ohsome.org/ohsome-api/stable/endpoints.html
- ohsome API documentation on the `filter` parameter: 
  https://docs.ohsome.org/ohsome-api/stable/filter.html

Second translate the query parameters into a layer definition and extent the file 
`workers/ohsome_quality_analyst/ohsome/layer_definitions.yaml`.

Thirdly specify for which indicator class this layer definition is a valid input. Add 
those indicator/layer combinations to the `INDICATOR_LAYER` tuple in the 
`workers/ohsome_quality_analyst/utils/definitions.py` module. The tuple consists of the 
indicator class name and the layer definitions key as strings (E.g. 
`("GhsPopComparisonBuildings", "building_count")`). If the specification was 
successfully added to the tuple it is shown in the return of the command 
`oqt list-layers`.

At last run `oqt create-inidicator --layer-name new-layer [...]` to check if the new layer can be used to make requests to the ohsome API and create an indicator successfully.
