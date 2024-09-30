#!/bin/bash

# requires the env variable $HURL_BASE_URL

rm -rf report
mkdir report

#hurl *.hurl --report-html report
hurl buildingcount_bbox_attributecompleteness.hurl --report-html report


printf "\n\nhurl report: file://$PWD/report/index.html\n"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  xdg-open report/index.html
elif [[ "$OSTYPE" == "darwin"* ]]; then
  open report/index.html
else
  printf "\nOS could not be detected. Please open report manually!\n"
fi