import http

import aiohttp
import pytest
from settings import settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"pattern": "Angela", "page_size": 5, "page_number": 1},
                {"status": http.HTTPStatus.OK, "length": 1}
        ),
        (
                {"pattern": "Turner", "page_size": 5, "page_number": 1},
                {"status": http.HTTPStatus.OK, "length": 2}
        ),
        (
                {"pattern": "Bob", "page_size": 5, "page_number": 1},
                {"status": http.HTTPStatus.NOT_FOUND, "length": 1}
        ),
        (
                {"page_size": 5, "page_number": -1},
                {"status": http.HTTPStatus.UNPROCESSABLE_ENTITY, "length": 1}
        )
    ]
)
async def test_list(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + "/api/v1/persons/search/"

    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"pattern": "Angela", "page_size": 5, "page_number": 3},
                {"status": http.HTTPStatus.NOT_FOUND}
        ),
        (
                {"pattern": "Angela", "page_size": 5, "page_number": -1},
                {"status": http.HTTPStatus.UNPROCESSABLE_ENTITY}
        )
    ]
)
async def test_wrong_page(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + "/api/v1/persons/search/"

    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()

    assert status == expected_answer["status"]
