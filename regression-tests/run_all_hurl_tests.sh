rm -rf report
mkdir report

export HURL_base_url=https://api.quality.ohsome.org/v1-test

hurl *.hurl   --report-html report

echo "\n\nhurl report: file://$PWD/report/index.html"

# mac only:
# open report/index.html