#!/bin/bash

export HURL_BASE_URL=http://127.0.0.1:8080

cd "$(dirname "$0")"
./__run_hurl_tests_for_stage.sh