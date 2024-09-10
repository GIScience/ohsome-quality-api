# Regression tests with hurl

Hurl is an HTTP command line client and HTTP test tool:

https://hurl.dev

In order to run the HTTP tests in this directory, `hurl` must be installed.
The tests can be run against the different stages using the following scripts:

* [run_hurl_tests_DEV.sh](./run_hurl_tests_DEV.sh)
* [run_hurl_tests_TEST.sh](./run_hurl_tests_TEST.sh)
* [run_hurl_tests_PROD.sh](./run_hurl_tests_PROD.sh)

Please note that you may get different results depending on the supported endpoints and connected spatial database of the system running on a given stage.

An HTML-report with the results is generated here:

[report/index.html](./report/index.html)


