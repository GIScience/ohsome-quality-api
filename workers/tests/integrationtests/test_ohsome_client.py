import asyncio
from datetime import datetime
from unittest import TestCase

from ohsome_quality_analyst.ohsome import client as ohsome_client

from .utils import oqt_vcr


class TestOhsomeClient(TestCase):
    @oqt_vcr.use_cassette()
    def test_get_latest_ohsome_timestamp(self):
        time = asyncio.run(ohsome_client.get_latest_ohsome_timestamp())
        self.assertIsInstance(time, datetime)
