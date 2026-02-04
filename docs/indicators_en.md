# Indicators

## Mapping Saturation

Calculate the saturation within the last 3 years.
Time interval is one month since 2008.


Different statistical models are used to find out if saturation is reached.

### Methods and Data

- Intrinsic approach.

Premise:

The added number of OSM objects of a specific feature class per time period decreases as the
number of mapped objects converges against the (unknown) true number of objects.

Each aggregation of features (e.g. length of roads or count of building)
has a maximum. After increased mapping activity saturation is reached near this
maximum.

### Limitations
- different meaningful for different indicators
  - better for small/ punctual object (houses)
  - worse for big polygons (land use -> one abrupt mapping step -> low completeness)
  - 

### References

- Gröchenig S et al. (2014): Digging into the history of VGI data-sets: results from
    a worldwide study on OpenStreetMap mapping activity
    (https://doi.org/10.1080/17489725.2014.978403)
- Barrington-Leigh C and Millard-Ball A (2017): The world’s user-generated road map
    is more than 80% complete
    (https://doi.org/10.1371/journal.pone.0180698 pmid:28797037)
- Josephine Brückner, Moritz Schott, Alexander Zipf, and Sven Lautenbach (2021):
    Assessing shop completeness in OpenStreetMap for two federal states in Germany
    (https://doi.org/10.5194/agile-giss-2-20-2021)


## Land Cover Completeness

Percentage of total area that is covered by OpenStreetMap land cover data.

### Methods and Data
- Intrinsic approach.

The ratio is computed by dividing the total area of the area of interest by the sum of the areas of all land cover polygons it contains.

### Limitations

Overlapping OSM land cover polygons will be counted multiple times and falsely improve the land cover completeness ratio.



## Land Cover Thematic Accuracy

Thematic accuracy of OpenStreetMap land cover data in comparison to the CORINE Land Cover (CLC) dataset.
This indicator can be calculated for multiple or a single CLC class(es).

### Methods and Data
- Extrinsic approach.

#### CORINE Land Cover
In its current form, the [CORINE Land Cover (CLC)](https://land.copernicus.eu/en/products/corine-land-cover) product offers a pan-European land cover and land use
inventory with 44 thematic classes, ranging from broad forested areas to individual vineyards.
CORINE uses a 3-level nomenclature for land cover classes.
Here, we use the "CORINE Land Cover 5 ha, Stand 2021 (CLC5-2021)"
provided by the German Federal Agency for Cartography and Geodesy and
level 2 of the nomenclature (e.g. 1.1 Urban Fabric, 1.2 Industrial, commercial and transport units).

### Preprocessing:

OSM features are assigned a CLC class based on their tags as specified below. 
We calculate the intersection of OSM land cover polygons and CORINE land cover polygons.
The resulting polygons contain both the OSM CLC class and the CORINE class.

| CLC (level 2)                                        | OSM tags                                                                                                                                                                                | 
|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1.1 Urban Fabric                                     | `landuse in (residential, retail)`                                                                                                                                                      |
| 1.2 	Industrial, commercial and transport units      | `landuse in (industrial, commercial, port, railway, lock) or leisure in (marina)`                                                                                                       |
| 1.3 	Mine, dump and construction sites               | `landuse in (quarry, construction, landfill, brownfield)`                                                                                                                               |
| 1.4 	Artificial, non-agricultural vegetated areas    | `landuse in (recreation_ground, allotments, village_green, cemetery, grass) or leisure in (park, garden, pitch, golf_course, playground, stadium, recreation_ground, common, dog_park)` |
| 2.1 	Arable land                                     | `landuse in (greenhouse_horticulture, greenhouse, farmland, farmyard)`                                                                                                                  |
| 2.2 	Permanent crops                                 | `landuse in (vineyard, orchard)`                                                                                                                                                        |
| 2.3 	Pastures                                        | `landuse in (meadow)`                                                                                                                                                                   |
| 2.4 	Heterogeneous agricultural areas                | *For class 2.4 many of the OSM tags from 2.1 apply. Therefore class 2.4 is never assigned.*                                                                                             |
| 3.1 	Forests                                         | `landuse in (forest) or natural in (wood)`                                                                                                                                              |
| 3.2 	Scrub and/or herbaceous vegetation associations | `landuse in (greenfield) or natural in (grassland, scrub, heath, fell)`                                                                                                                 |
| 3.3 	Open spaces with little or no vegetation        | `natural in (beach, scree, shingle, bare_rock, sand, glacier, mud, glacier, rock, cliff, fill)`                                                                                         |
| 4.1 	Inland wetlands                                 | `natural in (wetland)`                                                                                                                                                                  |
| 4.2 	Maritime wetlands                               | `landuse in (salt_pond)`                                                                                                                                                                |
| 5.1 	Inland waters                                   | `natural in (water, pond) or landuse in (basin, reservoir)`                                                                                                                             |
| 5.2 	Marine waters                                   | *Marine waters are not mapped in OSM. Therefore class 5.2 is never assigned.*                                                                                                           |

#### Indicator Calculation:

For the area-of-interest we fetch and clip polygons from the preprocessing step.
Next, we create confusion matrix between OSM and CORINE CLS classes.
This is the basis for calculating precision, recall and F1 score.
These calculations consider the area / size of the land cover polygons.

### References

- Schultz, Michael, Janek Voss, Michael Auer, Sarah Carter, and Alexander Zipf. 2017. “Open Land Cover from OpenStreetMap and Remote Sensing.” International Journal of Applied Earth Observation and Geoinformation 63 (May): 206–13. https://doi.org/10.1016/j.jag.2017.07.014.


## Road Thematic Accuracy

### Methods and Data
- Extrinsic approach.

#### Basis-DLM

The Basic DLM is published by the German Federal Agency for Cartography and Geodesy and describes the topographical
objects of the landscape and the relief of the Earth's surface in vector format. The objects are defined by their spatial
location, geometric type, descriptive attributes, and relationships to other objects. Each object has a unique 
identification number throughout Germany. The roads from this dataset are used for this indicator.

| Attribute | OSM tags  | DLM attribute | Description                                      | 
|-----------|-----------|---------------|--------------------------------------------------|
 | name      | name, ref | NAM           | The name or reference of a road.                 |
 | surface   | surface   | OFM           | The material the surface of the road is made of. |
 | lanes     | lanes     | FSZ           | The amount of lanes on this road segment.        |
 | width     | width     | BRF           | The width of the road.                           |
 | oneway    | oneway    | FAR           | The direction of oneway streets.                 |

### Processing

OSM roads and DLM roads are matched using [map-matching-2](https://github.com/addy90/map-matching-2) with a Markov decision process–based model.
For the matched roads first the presence of each attribute in both datasets is checked. If they are present in both,
the values are compared. By default, the values are compared directly, but there are some exceptions:

#### Name

For the name, the [Lhevenstein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) was calculated. The names
were counted as a match when their Levensthein ratio was above 0.85.

#### Surface

For surface, OSM tags and DLM tags are matched. All OSM tags that are not in the following table, were counted as not matching.

| DLM value        | OSM tags                                                  |
|------------------|-----------------------------------------------------------|
| concrete         | concrete                                                  |
| bitumen, asphalt | asphalt                                                   |
| pavemed          | paving_stones, sett, brick, cobblestone, unhewn_cobblestone |
| rock, fragmented | fine_gravel, gravel, sand, compacted, pebblestone         |

#### Width

For the width, a tolerance of 1 m was applied.

#### Oneway

To check the direction of the road, the vector of both geometries is calculated. If both have the same sign it is counted as a match.


### References

- A. Wöltche, "Open source map matching with Markov decision processes: A new method and a detailed benchmark with existing approaches", Transactions in GIS, vol. 27, no. 7, pp. 1959–1991, Oct. 2023, doi: [10.1111/tgis.13107](https://onlinelibrary.wiley.com/doi/full/10.1111/tgis.13107).


## Attribute Completeness
Derive the ratio of OSM features with present attributes.

### Methods and Data
- intrinsic method

Calculates the percentage of features that contain a certain attribute.

### Limitation
Limited to one attribute.

## Building Comparison
Compares the total building area of OSM with the building area of two reference datasets.

### Methods and Data
- extrinsic method

The result is the ratio of the total area of buildings in OSM devided by the total area of buildings in the reference dataset.

Reference datasets:
- [EUBUCCO](https://docs.eubucco.com/): Europe wide building footprints, derived from administrative datasets.
- [Microsoft Buildings](https://planetarycomputer.microsoft.com/dataset/ms-buildings): Worldwide building footprints, derived from satellite imagery.

### Limitations
Compares only the overall square meters of building polygons of OSM and reference dataset, not the actual overlap.

## Currentness
Estimate currentness of features by classifying contributions based on topic specific temporal thresholds into three groups: up-to-date, in-between and out-of-date.
Estimate currentness of features by analyzing the distribution of their most recent contributions
- Determine up-to-date, in-between and out-of-date contributions.
- Classified into up-to-date, medium, outdated -> Features are considered up-to-date if
their last edit falls within a predefined short time window.
- Put contributions into three bins: (1) up-to-date (2) in-between and (3)
        out-of-date. The range of those bins are based on the topic.
        After binning determine the result class based on share of features in each bin.

## Road Comparison
Result is a ratio of the length of reference roads which are covered by OSM roads to the total length of reference roads.

### Methods and Data
- extrinsic method

Identifies corresponding road geometries in OSM and the reference dataset to calculate the ratio of matched road length.


Reference dataset: 
- [Microsoft Roads](https://github.com/microsoft/RoadDetections): Worldwide dataset of roads, derived from satellite imagery.


## User Activity
Calculates how many unique users contributed to a specific topic, grouped by month.


### Methods and Data
- intrinsic method

Monthly amount of unique users who edited a specific topic in the area of interest are derived for the entire time range of OSM.
Additionally, the median for the last 3 years are calculated as well as a regression line to see the current tendency of user activity.

### Limitations
Does not give information about data quality on its own but can be used additionally to other indicators.
