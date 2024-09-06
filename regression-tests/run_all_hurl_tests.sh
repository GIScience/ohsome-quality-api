rm -rf report
mkdir report

hurl *.hurl   --report-html report

open report/index.html