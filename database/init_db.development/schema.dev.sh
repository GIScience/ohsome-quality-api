#!/bin/bash
# SQL files will be executed on first start of the database container
set -e
if [[ $OQT_TEST_DB = False ]]; then
    wget https://downloads.ohsome.org/OQT/schema.dev.sql.gz
    gunzip schema.dev.sql.gz
    wget https://downloads.ohsome.org/OQT/hexcells.sql.gz
    gunzip hexcells.sql.gz
    wget https://downloads.ohsome.org/OQT/shdi.sql.gz
    gunzip shdi.sql.gz
fi
