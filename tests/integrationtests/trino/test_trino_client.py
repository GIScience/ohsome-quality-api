import os

import pytest

# TODO: use VCR class from test utils
import vcr
from approvaltests import verify

from ohsome_quality_api.trino import client

WORKING_DIR = os.path.dirname(os.path.abspath(__file__))


@pytest.fixture
def sql_highways_count():
    file_path = os.path.join(WORKING_DIR, "highways-count.sql")
    with open(file_path, "r") as file:
        return file.read()


@pytest.fixture
def sql_highways():
    file_path = os.path.join(WORKING_DIR, "highways.sql")
    with open(file_path, "r") as file:
        return file.read()


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_query_version():
    sql = "SELECT version()"
    results = await client.query(sql)
    assert isinstance(results, client.QueryResults)
    assert results.next_uri is not None


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_fetch_version():
    sql = "SELECT version()"
    query = await client.query(sql)
    results = await client.fetch(query)
    assert isinstance(results, tuple)
    verify(str(results))


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_fetch_highways(sql_highways, sql_highways_count):
    query = await client.query(sql_highways)
    results_highways = await client.fetch(query)

    query = await client.query(sql_highways_count)
    results_highways_count = await client.fetch(query)

    assert len(results_highways) == results_highways_count[0][0]


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_query_missing_schema_name():
    sql = "SELECT * FROM foo"
    query = await client.query(sql)
    with pytest.raises(client.TrinoError) as error:
        await client.fetch(query)
    verify(str(error.value))


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_query_missing_catalog_name():
    sql = "SELECT * FROM bar.foo"
    query = await client.query(sql)
    with pytest.raises(client.TrinoError) as error:
        await client.fetch(query)
    verify(str(error.value))


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_query_catalog_not_found():
    sql = "SELECT * FROM foobar.bar.foo"
    query = await client.query(sql)
    with pytest.raises(client.TrinoError) as error:
        await client.fetch(query)
    verify(str(error.value))


@pytest.mark.asyncio()
@vcr.use_cassette
async def test_query_syntax_error():
    sql = "SELECT * MORF foo"
    query = await client.query(sql)
    with pytest.raises(client.TrinoError) as error:
        await client.fetch(query)
    verify(str(error.value))
