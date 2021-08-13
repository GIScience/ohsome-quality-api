# Layer Adding Guide

## What is a layer?
In the OQT we use the term Layer to describe the result of an ohsome API query. The 
layer define the features for which an indicator is calculated within your specified 
area. In order to create indicators on features which we have not defined yet, you can 
specify and add your own custom layer.

The layers are defined with 4 attributes: A name and a description for documentation 
purposes and the ohsome API endpoint as well as filter for functionality.

### Where to find information on how to define the ohsome API endpoint and filter?
Information on how to define the endpoint and filter, which you need to state in your 
layer definition, can be found in the 
[ohsome API documentation](https://docs.ohsome.org/ohsome-api/stable/). There is a 
section on the different 
[API endpoints](https://docs.ohsome.org/ohsome-api/stable/endpoints.html#elements-aggregation)
as well as a section on how to use and combine the 
[filter](https://docs.ohsome.org/ohsome-api/v1/filter.html).

## How to add a custom layer
In order to add your custom layer to the OQT and make use of it via the command line, 
you have to add your definition in the file 
[workers/ohsome-quality-analyst/ohsome/layer-defintions.yaml](/workers/ohsome-quality-analyst/ohsome/layer-defintions.yaml)
in your locally cloned repository. 

Once this is done, you need to add the combinations of indicator names and your layer 
which you want to allow to the tuple `INDICATOR_LAYER` in the file 
[workers/ohsome-quality-analyst/utils/definitions.py](/workers/ohsome-quality-analyst/utils/definitions.py).
This Tuple already contains all other usable combinations of indicators and layer. Keep 
in mind that you need to add an entry to this tuple for each combination you want to 
use, however, you need to define the layer (in the first file) only once. 

After this is done, you can use your layer via the command line like any other layer, 
and it will be listed among the other layers if you call the indicator creation help 
(`oqt create-indicator --help`). 
