#!/bin/bash

export HURL_BASE_URL=https://api.quality.ohsome.org/v1

cd "$(dirname "$0")"
./__run_hurl_tests_for_stage.sh