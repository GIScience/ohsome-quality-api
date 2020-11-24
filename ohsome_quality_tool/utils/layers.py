# TODO: this should reflect the major categories/layers
#   ideally they will be useful for many indicators
#   specific reports might define a custom set of layers
#   and respective filters
#   ideally this list should be shorter
#   e.g. come up with roads, buildings, amenities, healthcare
#   as the main categories to consider


DEFAULT_LAYERS = {
    "mountain": "natural=peak",
    "gas_stations": "amenity=fuel",
    "parks": "leisure=park or boundary=national_park",
    "waterways": "natural=water or waterway=*",
    "health_fac_pharmacies": "amenity in (pharmacy, hospital)",
    "eduction": "amenity in (school, college, university)",
    "public_safety": "amenity in (police, fire_station)",
    "public_transport": "highway=bus_stop or railway=station",
    "hotel": "tourism=hotel",
    "attraction": "tourism=attraction",
    "restaurant": "amenity=restaurant",
    "townhall": "amenity=townhall",
    "shop": "shop=*",
}

LEVEL_1_LAYERS = {
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
