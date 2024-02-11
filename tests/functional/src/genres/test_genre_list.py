import aiohttp
import pytest
from settings import settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"page_size": 5, "page_number": 1},
                {"status": 200, "length": 5}
        ),
        (
                {"page_size": 5, "page_number": 2},
                {"status": 200, "length": 1}
        ),
        (
                {"page_size": 5, "page_number": 3},
                {"status": 404, "length": 1}
        )
    ]
)
@pytest.mark.asyncio
async def test_list(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + "/api/v1/genres/"
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
                {"page_size": 0, "page_number": 0},
                {"status": 422, "length": 5}
        ),
        (
                {"page_size": 5, "page_number": -1},
                {"status": 422}
        ),
        (
                {"page_size": -1, "page_number": 1},
                {"status": 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_validation(query_data, expected_answer, fill_elastic):
    """Tests that API validate the collecting data."""
    session = aiohttp.ClientSession()
    url = settings.app_url + "/api/v1/genres/"
    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()
    assert status == expected_answer["status"]
