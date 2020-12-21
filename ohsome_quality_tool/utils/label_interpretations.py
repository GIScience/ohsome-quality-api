# This module should hold all textual descriptions of the quality label
# that are used in the "text" field of the JSON response

# the descriptions here are derived from the module poi_dens.py
# within the sketchmap-fitness repo
POI_DENSITY_LABEL_INTERPRETATIONS = dict(
    green=("It is probably easy to orientate on OSM-based sketchmaps of this region."),
    yellow=(
        "It might be difficult to orientate on OSM-based sketchmaps of "
        "this region. There are not many orientation providing features available, "
        "you should explore, if participants can orientate properly."
    ),
    red=(
        "It is probably hard to orientate on OSM-based sketchmaps of this region. "
        "There are just few orientation providing features available, "
        "you should explore, if participants can orientate properly."
    ),
    undefined=("The quality level could not be calculated for this indicator."),
)

MAPPING_SATURATION_LABEL_INTERPRETATIONS = dict(
    green=(
        "Saturation has been reached. The data in this region seem quite saturated "
        "with a growth of data less than 3 % within the last 3 years. "
        "This indicates good quality in respect to completeness."
    ),
    yellow=(
        "Saturation not yet reached. The data in this region still seem to be in "
        "a growth stadium with a growth of data more than 3 % within the last 3 years. "
        "This indicates a difficult to specify quality in respect to completeness, "
        "because it depends on the growth rate over time. The growth could be "
        "near to saturated or still be in an high growth stadium."
    ),
    red=(
        "Saturation has not been reached at all. "
        "The mapping in this region are in just starting. "
        "With regard to completeness this means bad quality."
    ),
    undefined=(
        "The quality level could not be calculated for this indicator."
        "This is most likely due to the fact that no features have been mapped "
        "for this area of interest. Refer to other indicators that rely on "
        "an extrinsic comparison to identify if this means that data quality is "
        "bad or if there is just nothing to map here."
    ),
)


LAST_EDIT_LABEL_INTERPRETATIONS = dict(
    green=(
        "This is a rather high value and indicates that the map features "
        "are very unlike to be outdated. This refers to good data quality in "
        "respect to currentness."
    ),
    yellow=(
        "Some map features could be outdated in this regions, since only a smaller "
        "fraction has been updated in the past year. "
        "This refers to medium data quality in respect to currentness."
    ),
    red=(
        "The vast majority of map features has not been updated in the last year. "
        "Be aware that there it is very likely that many map features are outdated. "
        "You should carefully check this before using the data as it indicates bad "
        "data quality in respect to currentness."
    ),
    undefined=(
        "The quality level could not be calculated for this indicator."
        "This is most likely due to the fact that no features have been mapped "
        "for this area of interest. Refer to other indicators that rely on "
        "an extrinsic comparison to identify if this means that data quality is "
        "bad or if there is just nothing to map here."
    ),
)


GHSPOP_COMPARISON_LABEL_INTERPRETATIONS = dict(
    green=(
        "For the given population density, this is a relatively high value and "
        "indicates a good data quality in terms of completeness."
    ),
    yellow=(
        "The comparison between population density and building density indicate "
        "that there are still unmapped buildings. This results in a medium "
        "data quality in respect to completeness."
    ),
    red=(
        "The comparison of population density and building density shows, that "
        "a majority of buildings has not been mapped yet. This results in a bad "
        "data quality in respect to completeness"
    ),
    undefined=("The quality level could not be calculated for this indicator."),
)


GUF_COMPARISON_LABEL_INTERPRETATIONS = dict(
    green=(
        "This is a relatively high value and refers to  a good data quality "
        "in respect to completeness"
    ),
    yellow=(
        "This indicates, that some of the map features for this region"
        "are still missing. This refers to a medium data quality in respect"
        "to completeness"
    ),
    red=(
        "This indicates, that there is a relatively high amount "
        "of unmapped buildings and refers to a bad data quality in respect "
        "to completeness."
    ),
    undefined=("The quality level could not be calculated for this indicator."),
)
