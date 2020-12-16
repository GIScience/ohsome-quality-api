# This module should hold all textual descriptions of the quality label
# that are used in the "text" field of the JSON response

# the descriptions here are derived from the module poi_dens.py
# within the sketchmap-fitness repo
POI_DENSITY_LABEL_INTERPRETATIONS = \
    dict(green="It is probably easy to orientate on OSM-based sketchmaps "
               "of this region.",
         yellow="It might be difficult to orientate on OSM-based sketchmaps of "
                "this region. There are not many orientation providing features available, "
                "you should explore, if participants can orientate properly.",
         red="It is probably hard to orientate on OSM-based sketchmaps of this region. "
             "There are just few orientation providing features available, you should explore, "
             "if participants can orientate properly.")

MAPPING_SATURATION_LABEL_INTERPRETATIONS = \
    dict(green="Saturation reached. The data in this region seem quite saturated "
               "with a growth of data less than 3 % within the last 3 years. " 
               "This indicates good quality in respect to completeness.",
         yellow="Saturation not yet reached. The data in this region still seem to be in a growth stadium  "
               "with a growth of data more than 3 % within the last 3 years. "
               "This indicates a difficult to sepcify quality in respect to completeness, "
               "because it depends on the growth rate over time. The growth could be "
               "near to saturated or still be in an high growth stadium.",
         red="No Saturation at all. The data in this region are in a start stadium. With regard "
               "to completeness, this means bad quality.")