#!/usr/bin/env bash
# This scripts is used to dump schema and tables
# for a minimal local development setup for OQT.

psql -f create_dev_schema.sql
pg_dump --schema=development --schema=admin > schema.sql
psql -f remove_dev_schema.sql
