# TODO: this should reflect the major categories/layers
#   ideally they will be useful for many indicators
#   specific reports might define a custom set of layers
#   and respective filters
#   ideally this list should be shorter
#   e.g. come up with roads, buildings, amenities, healthcare
#   as the main categories to consider


LEVEL_ONE_LAYERS = {
    "waterways": {
        "filter": "natural=water or waterway=*",
        "unit": "length",
    },
    "buildings": {"filter": "building=*", "unit": "count"},
    "major_roads": {
        "filter": "highway in (motorway, trunk, primary, secondary, tertiary, unclassified, residential)",  # noqa
        "unit": "length",
    },
    "roads": {"filter": "highway=*", "unit": "length"},
}


SKETCHMAP_FITNESS_POI_LAYER = {
    "mountain": {"filter": "natural=peak", "unit": "count"},
    "gas_stations": {"filter": "amenity=fuel", "unit": "count"},
    "parks": {"filter": "leisure=park or boundary=national_park", "unit": "count"},
    "waterways": {"filter": "natural=water or waterway=*", "unit": "count"},
    "health_fac_pharmacies": {
        "filter": "amenity in (pharmacy, hospital)",
        "unit": "count",
    },
    "eduction": {"filter": "amenity in (school, college, university)", "unit": "count"},
    "public_safety": {"filter": "amenity in (police, fire_station)", "unit": "count"},
    "public_transport": {
        "filter": "highway=bus_stop or railway=station",
        "unit": "count",
    },
    "hotel": {"filter": "tourism=hotel", "unit": "count"},
    "attraction": {"filter": "tourism=attraction", "unit": "count"},
    "restaurant": {"filter": "amenity=restaurant", "unit": "count"},
    "townhall": {"filter": "amenity=townhall", "unit": "count"},
    "shop": {"filter": "shop=*", "unit": "count"},
}


SKETCHMAP_FITNESS_FEATURES = {
    "highways": {"filter": "highway=*", "unit": "length"},
    "amenities": {"filter": "amenity=*", "unit": "count"},
}
