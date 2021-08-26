# Layer

A layer describes the request which should be made to the [ohsome API](https://docs.ohsome.org/ohsome-api/v1/). Each layer is representative of a specific set of features, aggregated informations or user statistics derived from the OpenStreetMap database. Each layer is defined by the ohsome API parameters `endpoint` and `filter`. In addition each layer definition has a key, name and description. Layer definitions are written down as YAML file: `workers/ohsome_quality_analyst/ohsome/layer_defintions.yaml`

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

First create an ohsome API query to retrieve desired information from the ohsome API. Helpful resources for this task are:
- Interactive ohsome API interface: https://api.ohsome.org/v1/swagger-ui.html
- ohsome API documentation on the `endpoint` parameter: https://docs.ohsome.org/ohsome-api/stable/endpoints.html
- ohsome API documentation on the `filter` parameter: https://docs.ohsome.org/ohsome-api/stable/filter.html

Second translate the query parameters into a layer definition and extent the file `workers/ohsome_quality_analyst/ohsome/layer_definitions.yaml`.

Thirdly specify for which indicator class this layer definition is a valid input. Add those indicator/layer combinations to the `INDICATOR_LAYER` tuple in the `workers/ohsome_quality_analyst/utils/defintions.py` module. The tuple consists of the indicator class name and the layer definitions key as strings (E.g. `("GhsPopComparisonBuildings", "building_count")`).

Check if everything was successful by running `oqt list-layers`.
