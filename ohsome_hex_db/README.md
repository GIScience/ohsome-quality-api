# Database

The database represents a part of the official ohsomehex database.
To build this database three SQL scripts are required:

- postgis-raster.sql: Enable raster driver.
- [admin-schema.sql](https://gitlab.gistools.geog.uni-heidelberg.de/giscience/big-data/ohsome/apps/hex/ohsomehex-db): Official schema of the ohsomehex database.
- ohsome-hex-isea.sql: SQL dump of two tables representing the hex grids at two zoom levels.
    - Excluded in this repository due to size
    - The script which has been used to create this dump can be found at `scripts/create_isea_dump.sh`


```bash
docker build .
docker run \
    -d \
    -p 5445:5432 \
    -e POSTGRES_PASSWORD="xxx" \
    -e POSTGRES_USER="hexadmin" \
    -v pg_data:/var/lib/postgresql/data \
    image_id
```


Make sure the port is open:

```bash
sudo iptables -I INPUT -p tcp --dport 5445 -j ACCEPT
```
