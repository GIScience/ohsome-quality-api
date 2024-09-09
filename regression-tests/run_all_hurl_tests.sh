rm -rf report
mkdir report

hurl *.hurl   --report-html report

echo "hurl report: file://$PWD/report/index.html"

# mac only:
# open report/index.html