#!/bin/bash
set -e

if [[ $OQT_TEST_DB = False ]]; then
    wget https://downloads.ohsome.org/OQT/schema.dev.sql.gz
    gunzip schema.dev.sql.gz
fi
