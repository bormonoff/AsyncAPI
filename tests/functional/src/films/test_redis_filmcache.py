import http

import aiohttp
import pytest
import settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, result",
    [
        (
            {"film_id": "ba1f77d3-8df0-48dd-a8c1-1266ad9cc1b9"},
            {"status": http.HTTPStatus.OK}
        )
    ]
)
async def test_search(query_data, result, create_es_indices):
    "Tests that API get's a film from cache if elastic is unavailable."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + f"/api/v1/films/{query_data['film_id']}"

    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()

    assert status == result["status"]


@pytest.mark.parametrize(
    "query_data, body_count",
    [
        (
            {"sort": "imdb_rating", "genre": "horror", "page_size": "10", "page_number": "1"},
            7
        )
    ]
)
async def test_out_of_range(query_data, body_count):
    "Tests that page count is correct."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/"

    async with session.get(url, params=query_data) as response:
        body = await response.json()
    await session.close()

    assert len(body) == body_count
