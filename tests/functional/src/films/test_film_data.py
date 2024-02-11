import aiohttp
import pytest
import settings


@pytest.mark.parametrize(
    "query_data, result",
    [
        (
            {"film_id": "ba1f77d3-8df0-48dd-a8c1-1266ad9cc1b9"},
            {"status": 200}
        ),
        (
            {"film_id": "00000000-0000-0000-0000-000000000000"},
            {"status": 404}
        ),
    ]
)
@pytest.mark.asyncio
async def test_search(query_data, result, fill_elastic):
    "Tests that API responses are correct."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + f"/api/v1/films/{query_data['film_id']}"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    assert status == result["status"]

