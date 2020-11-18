#!/usr/bin/env bash

gzip -d /data/isea3h_world_res_6_hex.sql.gz
gzip -d /data/isea3h_world_res_12_hex.sql.gz
gzip -d /data/nuts_rg_01m_2021.sql
gzip -d /data/nuts_rg_60m_2021.sql
gzip -d /data/ghs_pop.sql

psql -U $POSTGRES_USER -f /data/isea3h_world_res_6_hex.sql
psql -U $POSTGRES_USER -f /data/isea3h_world_res_12_hex.sql
psql -U $POSTGRES_USER -f /data/nuts_rg_01m_2021.sql
psql -U $POSTGRES_USER -f /data/nuts_rg_60m_2021.sql
psql -U $POSTGRES_USER -f /data/ghs_pop.sql