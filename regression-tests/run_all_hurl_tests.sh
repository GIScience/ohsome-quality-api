rm -rf report
mkdir report

hurl *.hurl   --report-html report

echo "\n\nhurl report: file://$PWD/report/index.html"

# mac only:
# open report/index.html