# Indicators

This document gives an overview of the available "core" indicators, methods and data being used, how to interpret the result and references to scientific literature and other resources. Each indicator provides a quality estimation in form of a label.

## Mapping Saturation

Calculate if mapping has saturated. Different statistical models are used to find out if saturation is reached. High saturation has been reached if the growth of the fitted curve is minimal.

### Methods and Data

*Approach:* Intrinsic

*Data:* OSM

*Time*: 2008 until latest
 
*Premise*: Each aggregation of features (e.g. length of roads or count of buildings) has a maximum. After increased mapping activity saturation is reached near this maximum. In other words: Over time number of objects added to OSM decreases as the number of mapped objects converges against the true number of objects.

*Model selection criteria*:
1. Decrease in curve growth
    - The last data point should be after the inflection point of the curve
    - If no inflection point exists other measures are used which approximates 50% of asymptote.
2. Data is below 95% confidence interval of the asymptote
    - Check if the latest data (average last two years) is lower than the upper limit of the 95% confidence interval of the estimated asymptote


### Result

*Result value (`result.value`):* Saturation (gradient) of the best fitting curve over the last three years.

*High threshold*: above or equal 97 % of saturation correlates with high completeness

*Low threshold*: below or equal 30 % of saturation correlates with low completeness


### References

*Scientific Papers:*
- Josephine Brückner, Moritz Schott, Alexander Zipf, and Sven Lautenbach (2021):
    Assessing shop completeness in OpenStreetMap for two federal states in Germany
    (https://doi.org/10.5194/agile-giss-2-20-2021)
- Barrington-Leigh C and Millard-Ball A (2017): The world’s user-generated road map
    is more than 80% complete
    (https://doi.org/10.1371/journal.pone.0180698 pmid:28797037)
- Gröchenig S et al. (2014): Digging into the history of VGI data-sets: results from
    a worldwide study on OpenStreetMap mapping activity
    (https://doi.org/10.1080/17489725.2014.978403)


## Currentness

TODO


## Building Comparison

### Method and Data

*Approach:* Extrinsic

*Data:* OSM, EUBUCO, Microsoft Buildings

*Time:* Latest

*Premise:* OSM should have similar building area as reference datasets. Too low? Too high?


### Result

*Result value (`result.value`):* Ratio of OSM building area to reference data building area

*High threshold*: above or equal 80 % correlates with high completeness

*Low threshold*: below or equal 20 % correlates with low completeness
