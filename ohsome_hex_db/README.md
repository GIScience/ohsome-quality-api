# Database

This database represents a part of the official ohsomehex database.


## Information

Information on scripts for database initialization:

- ohsome-hex-isea.sql: SQL dump of two tables representing the hex grids at two zoom levels.
    - Excluded in this repository due to size
    - The script which has been used to create this dump can be found at `scripts/create_isea_dump.sh`


## Building


```bash
docker build Dockerfile.prod
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
