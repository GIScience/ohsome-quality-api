#!/bin/bash
# Import GUF04 data from existing database into another.

PGPASSWORD="mypassword" pg_dump \
    -no-owner \
    --no-privileges \
    -h localhost \
    -p 5432 \
    -U postgres \
    -t guf04 pop \
    | \
    psql -h localhost -p 5445 -U hexadmin hexadmin
