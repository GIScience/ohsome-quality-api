#!/usr/bin/env bash
# This scripts is used to dump schema and tables
# for a minimal local development setup for OQT.

psql -f remove_dev_schema.sql
psql -f create_dev_schema.sql
pg_dump --schema=test --schema=admin > schema.test.sql
pg_dump --schema=development > schema.dev.sql
gzip schema.dev.sql
psql -f remove_dev_schema.sql
