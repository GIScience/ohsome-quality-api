#!/usr/bin/env bash
# This scripts is used to dump schema and tables
# for a minimal local development setup for OQT.

pg_dump --schema=development --schema=admin > schema.sql
pg_dump \
    --table=oqt_regions \
    --table=oqt_regions_ogc_fid_seq \
    --table=oqt_regions_geom_geom_idx \
    --table=oqt_regions_pkey \
    > test-regions.sql
