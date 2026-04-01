import asyncio
import unittest

from ohsome_quality_api.utils import helper_asyncio


class TestHelper(unittest.TestCase):
    async def bar(self):
        raise ValueError()

    async def foo(self):
        return "OK"

    def setUp(self):
        self.tasks = [
            self.foo(),
            self.foo(),
            self.foo(),
            self.foo(),
            self.foo(),
        ]

    def test_gather_with_semaphore(self):
        results = asyncio.run(helper_asyncio.gather_with_semaphore(self.tasks))
        assert results == ["OK", "OK", "OK", "OK", "OK"]

    def test_gather_with_semaphore_return_exceptions(self):
        results = asyncio.run(
            helper_asyncio.gather_with_semaphore(self.tasks, return_exceptions=True)
        )
        assert results == ["OK", "OK", "OK", "OK", "OK"]

    def test_gather_with_semaphore_return_exceptions_error(self):
        tasks = [*self.tasks, self.bar()]
        results = asyncio.run(
            helper_asyncio.gather_with_semaphore(tasks, return_exceptions=True)
        )
        assert len(results) == 6
        assert isinstance(results[-1], ValueError)

    def test_filter_exceptions(self):
        tasks = [*self.tasks, self.bar()]
        results = asyncio.run(
            helper_asyncio.gather_with_semaphore(tasks, return_exceptions=True)
        )
        exceptions = helper_asyncio.filter_exceptions(results)
        assert len(exceptions) == 1
        assert isinstance(exceptions[0], ValueError)
