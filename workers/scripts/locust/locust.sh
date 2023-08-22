#!/bin/bash

today=$(date +"%Y-%m-%d")
locust \
    --autostart \
    --autoquit 0 \
    --host https://oqt.ohsome.org/api \
    --users 10 \
    --run-time 10m \
    --html "$today"-locust-report.html \
    --csv "$today"-locust

