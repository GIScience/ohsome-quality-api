#!/usr/bin/env bash
# This scripts is used to dump schema and tables
# for a minimal local development setup for OQT.

pg_dump --schema=development --schema=admin > schema.sql
pg_dump \
    --table=test_regions \
    --table=test_regions_ogc_fid_seq \
    --table=test_regions_geom_geom_idx \
    --table=test_regions_pkey \
    > test-regions.sql
