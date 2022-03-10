# Raster datasets (Stored as file on Disk)

OQT operates on raster datasets stored on disk.


## Location (Data directory)

The raster files are located in the `data` directory at the root of git repository.

The location can be changed by setting the environment variable `$OQT_DATA_DIR`.

For testing purposes the `data` directory at the root of the git repository contains raster files *clipped* to the extent of Heidelberg.
The `data` directory is listed in `.gitignore`. This way the original raster files in full size can be stored in this directory for development.

The following section will describe how to set up the individual raster datasets.


## Setup


### GHS-BUILT R2018A

Information:
- https://ghsl.jrc.ec.europa.eu/ghs_bu2019.php
- product: GHS-BUILT, epoch: 2015, resolution: 1 km, coordinate system: Mollweide.

Setup steps:
1. Download the global raster as single file at [https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_LDSMT_GLOBE_R2018A/GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K/V2-0/GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.zip](https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_BUILT_LDSMT_GLOBE_R2018A/GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K/V2-0/GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.zip)
2. Extract archive
3. Move `GHS_BUILT_LDS2014_GLOBE_R2018A_54009_1K_V2_0.tif` to the OQT data directory


### GHS-POP R2019A

Information:
- https://ghsl.jrc.ec.europa.eu/ghs_pop2019.php
- product: GHS-POP, epoch: 2015, resolution: 1 km, coordinate system: Mollweide.

Setup steps:
1. Download the global raster as single file at [https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_MT_GLOBE_R2019A/GHS_POP_E2015_GLOBE_R2019A_54009_1K/V1-0/GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.zip](https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_MT_GLOBE_R2019A/GHS_POP_E2015_GLOBE_R2019A_54009_1K/V1-0/GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.zip)
2. Extract archive
3. Move `GHS_POP_E2015_GLOBE_R2019A_54009_1K_V1_0.tif` to the OQT data directory


### GHS-SMOD R2019A

Information:
- https://ghsl.jrc.ec.europa.eu/ghs_smod2019.php
- product: GHS-SMOD, epoch: 2015, resolution: 1 km, coordinate system: Mollweide.

Setup steps:
1. Download the global raster as single file at [https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_SMOD_POP_GLOBE_R2019A/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K/V2-0/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.zip](https://cidportal.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_SMOD_POP_GLOBE_R2019A/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K/V2-0/GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.zip)
2. Extract archive
3. Move `GHS_SMOD_POP2015_GLOBE_R2019A_54009_1K_V2_0.tif` to the OQT data directory


### Nighttime Lights VIIRS - Annual VNL V2

Information:
- https://eogdata.mines.edu/products/vnl/
- product: Annual VNL V2, epoch: 2020, resolution: 15 arc second (~500m at the Equator), coordinate system: EPSG:4326 (Geographic Latitude/Longitude)
- note: You will need to register a account at EOG to download this dataset

Setup steps:
1. Download the global raster as single file at [https://eogdata.mines.edu/nighttime_light/annual/v20/2020/](https://eogdata.mines.edu/nighttime_light/annual/v20/2020/)
    - The filename is `VNL_v2_npp_2020_global_vcmslcfg_c202102150000.average_masked.tif.gz`
2. Extract the archive
3. Move `VNL_v2_npp_2020_global_vcmslcfg_c202102150000.average_masked.tif` to the OQT data directory
