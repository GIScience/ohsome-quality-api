#!/usr/bin/env bash

pg_dump -U hexadmin --data-only -t development.isea3h_world_res_6_hex -v -h localhost -p 5445 > isea3h_world_res_6_hex.sql
pg_dump -U hexadmin --data-only -t development.isea3h_world_res_12_hex -v -h localhost -p 5445 > isea3h_world_res_12_hex.sql

pg_dump -U hexadmin --data-only -t development.nuts_rg_01m_2021 -v -h localhost -p 5445 > nuts_rg_01m_2021.sql
pg_dump -U hexadmin --data-only -t development.nuts_rg_60m_2021 -v -h localhost -p 5445 > nuts_rg_60m_2021.sql

pg_dump -U hexadmin --data-only -t development.ghs_pop -v -h localhost -p 5445 > ghs_pop.sql

gzip isea3h_world_res_6_hex.sql
gzip isea3h_world_res_12_hex.sql

gzip nuts_rg_01m_2021.sql
gzip nuts_rg_60m_2021.sql

gzip ghs_pop.sql





