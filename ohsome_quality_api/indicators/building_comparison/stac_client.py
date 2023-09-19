import dask_geopandas
import deltalake
import geojson
import mercantile
import planetary_computer
import pystac_client
from shapely import polygons
from shapely.geometry import box


def get_area(aoi):
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    collection = catalog.get_collection("ms-buildings")
    asset = collection.assets["delta"]

    storage_options = {
        "account_name": asset.extra_fields["table:storage_options"]["account_name"],
        "sas_token": asset.extra_fields["table:storage_options"]["credential"],
    }
    table = deltalake.DeltaTable(asset.href, storage_options=storage_options)

    coords_list = list(geojson.utils.coords(aoi))
    box_coords = []
    for i in (0, 1):
        res = sorted(coords_list, key=lambda x: x[i])
        box_coords.append((res[0][i], res[-1][i]))
    bbox = box(box_coords[0][0], box_coords[1][0], box_coords[0][1], box_coords[1][1])

    quadkeys = [
        int(mercantile.quadkey(tile))
        for tile in mercantile.tiles(*bbox.bounds, zooms=9)
    ]
    file_uris = table.file_uris([("quadkey", "in", quadkeys)])

    df = dask_geopandas.read_parquet(file_uris, storage_options=storage_options)
    clip_feature = polygons(aoi.geometry.coordinates)
    df = df.clip(clip_feature[0])
    # TODO: get suitable CRS for area of interest (gdf.estiate_utm_crs())
    df = df.to_crs(25832)
    return df.geometry.area.compute().sum()
