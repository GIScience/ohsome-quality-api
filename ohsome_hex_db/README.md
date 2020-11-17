# Database

```bash
docker build .
docker run \
    -d \
    -e POSTGRES_PASSWORD="xxx" \
    -e POSTGRES_USER="hexadmin" \
    -v pg_data:/var/lib/postgresql/data \
    image_id
```
