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

| indicator                      | `--jobs=1 --repeat 1` | `--jobs 15 --repeat 10` | `--jobs 15 --repeat 100`          |
|--------------------------------|-----------------------|-------------------------|-----------------------------------|
| land-cover-thematic-accuracy   | 15547 ms              | 18217 ms                | 134782 ms                         |
| land-cover-completeness        | 29146 ms              | 45915 ms                | 386117 ms                         |
| currentness roads-all-highways | 251577 ms             | 129851 ms               | 1375128 ms (some requests run in ohsome API timeout) |
| currentness roads (cars)       | 51694 ms              | 129010 ms               | 608232 ms                         |
| currentness building-count     | 41324 ms              | 88242 ms                | 461576 ms                         |



