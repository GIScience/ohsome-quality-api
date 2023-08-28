#!/usr/bin/env bash

cd "$(dirname "$0")"/../ohsome_quality_api/api/static && \
  wget https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js -O swagger-ui-bundle.js && \
  wget https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css -O swagger-ui.css && \
  wget https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js -O redoc.standalone.js
