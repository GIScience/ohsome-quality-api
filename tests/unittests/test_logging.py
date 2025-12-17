import logging


def test_logging_default(caplog):
    logger = logging.getLogger("ohsome_quality_api")
    logger.info("foo")
    logger.debug("bar")
    assert len(caplog.records) == 1
