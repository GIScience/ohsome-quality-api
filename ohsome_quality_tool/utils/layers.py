# TODO: this should reflect the major categories/layers
#   ideally they will be useful for many indicators
#   specific reports might define a custom set of layers
#   and respective filters
#   ideally this list should be shorter
#   e.g. come up with roads, buildings, amenities, healthcare
#   as the main categories to consider
from ohsome_quality_tool.utils.definitions import LayerDefinition

BUILDING_COUNT_LAYER = LayerDefinition(
    name="building-count",
    description="All buildings as defined by all objects tagged with 'building=*'.",
    filter="building=*",
    unit="count",
)


BUILDING_AREA_LAYER = LayerDefinition(
    name="building-area",
    description="All buildings as defined by all objects tagged with 'building=*'.",
    filter="building=*",
    unit="area",
)


MAJOR_ROADS_LAYER = LayerDefinition(
    name="major-roads",
    description=(
        "The road network defined by all objects which hold the principal tags for "
        "the road network as defined in the OSM Wiki: "
        "https://wiki.openstreetmap.org/wiki/Key:highway"
    ),
    filter=(
        "highway in (motorway, trunk, primary, secondary, "
        "tertiary, unclassified, residential)"
    ),
    unit="length",
)


AMENITIES_LAYER = LayerDefinition(
    name="amenities",
    description="All features with the amenities key.",
    filter="amenity=*",
    unit="count",
)


POI_LAYER = LayerDefinition(
    name="points-of-interests",
    description=(
        "A lot of different objects such related to natural features "
        "transportation and amenities in a city."
    ),
    filter=(
        "natural=peak or leisure=park or boundary=national_park or "
        "natural=water or waterway=* or highway=bus_stop or railway=station or "
        "shop=* or tourism in (hotel, attraction) or "
        " amenity in (fuel, pharmacy, hospital, school, college, university, "
        "police, fire_station, restaurant, townhall)"
    ),
    unit="count",
)


def get_all_layer_definitions():
    """Returns all layer definitions"""
    return {
        "points-of-interests": POI_LAYER,
        "building-count": BUILDING_COUNT_LAYER,
        "building-area": BUILDING_AREA_LAYER,
        "major-roads": MAJOR_ROADS_LAYER,
        "amenities": AMENITIES_LAYER,
    }
