# Regression tests with hurl

Hurl is an HTTP command line client and HTTP test tool:

https://hurl.dev

In order to run the HTTP tests in this directory, `hurl` must be installed.

## Usage

The tests can be run against the different stages using the following scripts:

* [run_hurl_tests_DEV.sh](./run_hurl_tests_DEV.sh)
* [run_hurl_tests_TEST.sh](./run_hurl_tests_TEST.sh)
* [run_hurl_tests_PROD.sh](./run_hurl_tests_PROD.sh)

Please note that you may get different results depending on the supported endpoints and connected spatial database of the system running on a given stage.

An HTML-report with the results is generated here:

[report/index.html](./report/index.html)


## Benchmarking

```sh
hurl --test --jobs 1 --repeat 1 --variable BASE_URL="https://api.quality.ohsome.org/v1-test/" land-cover-thematic-accuracy.hurl
```

### Release 1.10

| indicator                      | `--jobs=1 --repeat 1` | `--jobs 15 --repeat 10` | `--jobs 15 --repeat 100`                          |
|--------------------------------|-----------------------|-------------------------|---------------------------------------------------|
| land-cover-thematic-accuracy   | 15.547 s              | 18.217 s                | 134.782 s                                         |
| land-cover-completeness        | 29.146 s              | 45.915 s                | 386.117 s                                         |
| currentness roads-all-highways | 251.577 s             | 129.851 s               | 1375.128 s (some requests run in ohsome API timeout) |
| currentness roads (cars)       | 51.694 s              | 129.010 s               | 608.232 s                                         |
| currentness building-count     | 41.324 s              | 88.242 s                | 461.576 s                                         |



