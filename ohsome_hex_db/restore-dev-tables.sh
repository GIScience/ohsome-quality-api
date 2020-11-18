#!/usr/bin/env bash

gzip -d /data/isea3h_world_res_6_hex.sql.gz
gzip -d /data/isea3h_world_res_12_hex.sql.gz
gzip -d /data/nuts_rg_01m_2021.sql.gz
gzip -d /data/nuts_rg_60m_2021.sql.gz
gzip -d /data/ghs_pop.sql.gz

psql -U $POSTGRES_USER -f /data/isea3h_world_res_6_hex.sql
psql -U $POSTGRES_USER -f /data/isea3h_world_res_12_hex.sql
psql -U $POSTGRES_USER -f /data/nuts_rg_01m_2021.sql
psql -U $POSTGRES_USER -f /data/nuts_rg_60m_2021.sql
psql -U $POSTGRES_USER -f /data/ghs_pop.sql

wget https://heibox.uni-heidelberg.de/f/1d9a3249a30244b79492/?dl=1 --output-document=/data/guf04.dump
pg_restore -U $POSTGRES_USER -v --data-only -d $POSTGRES_DB /data/guf04.dump