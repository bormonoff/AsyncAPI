import aiohttp
import pytest
import settings


@pytest.mark.parametrize(
    "query_data, result",
    [
        (
            {"pattern": "Rock", "page_size": "10", "page_number": "1"},
            {"status": 200, "len": 2}
        ),
        (
            {"pattern": "Star", "page_size": "100", "page_number": "1"},
            {"status": 200, "len": 48}
        ),
        (
            {"pattern": "Star", "page_size": "10", "page_number": "4"},
            {"status": 200, "len": 10}
        ),
        (
            {"pattern": "Star", "page_size": "10", "page_number": "5"},
            {"status": 200, "len": 8}
        ),
        (
            {"pattern": "Theory", "page_size": "10", "page_number": "1"},
            {"status": 404, "len": 1}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search(query_data, result, fill_elastic):
    "Tests that API responses are correct."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/search/"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    assert status == result["status"]
    assert len(body) == result["len"]


@pytest.mark.parametrize(
    "query_data",
    [
        (
            {"pattern": "Rock", "page_size": "-1", "page_number": "1"}
        ),
        (
            {"pattern": "Star", "page_size": "1", "page_number": "-1"}
        ),
        (
            {"page_size": "1", "page_number": "1"}
        ),
    ]
)
@pytest.mark.asyncio
async def test_validation(query_data):
    "Tests that request data is valid."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/search/"
    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()
    assert status == 422