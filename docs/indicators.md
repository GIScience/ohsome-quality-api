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

#### Preprocessing:

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


## Land Cover Completeness

Percentage of total area that is covered by OpenStreetMap land cover data.


### Methods and Data
- Intrinsic approach.

The ratio is computed by dividing the total area of the area of interest by the sum of the areas of all land cover polygons it contains.

### Limitations

The are of overlapping OSM land cover polygons will be counted multiple times.
