import pystac

item_url = "https://planetarycomputer.microsoft.com/api/stac/v1/collections/ms-buildings/items/Germany_120203320_2023-04-25"

# Load the individual item metadata and sign the assets
item = pystac.Item.from_file(item_url)

# No data assets in this item, show the STAC data
item
breakpoint()
