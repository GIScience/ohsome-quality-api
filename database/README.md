# Database

This database is a PostGIS database.

The database contains serveral dataset including the hexagonal grids (isea_hex) from the official ohsomehex database.

## Setup

To setup the database a Dockerfile and scripts for initialization of the database are provided.

During the first run of the container following datasets are imported:

- ISEA_HEX
- GADM
- NUTS
- GHS_POP

> NOTE: Currently the `ohsome-hex-isea.sql` is not included in the git repository and has to be downloaded manually.

> NOTE 2: The script which has been used to create `ohsome-hex-isea.sql` dump can be found at `ohsome-quality-analyst/scripts/create_isea_dump.sh`


```bash
docker build --tag oqt-db --file Dockerfile.prod .
docker run \
    -d \
    -p 5432:5432 \
    -e POSTGRES_PASSWORD="mypassword" \
    -e POSTGRES_USER="hexadmin" \
    -v pg_data:/var/lib/postgresql/data \
    oqt-db
```

- Build time is roughly: `5 min`
- First run time is much longer


Make sure the port is open:

```bash
sudo iptables -I INPUT -p tcp --dport 5445 -j ACCEPT
```


## Import additional datasets.

Scripts to import additional datasets can be found at `ohsome-quality-analyst/scripts/import`. Those include the GlobalUrbanFootprint which is not part of the initial setup of the database due to size.

The packages `gdal-bin` and `postgis` need to be installed on the server for the import scripts.

> Note:
>
> The total size of GUF04 files are 32 GB.
> The total size of GUF04 table is 42 GB.
