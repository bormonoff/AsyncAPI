import http

import aiohttp
import pytest
from settings import settings

pytestmark = pytest.mark.asyncio

@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"genre_name": "History"},
                {"status": http.HTTPStatus.OK, "name": "History", "id": "eb7212a7-dd10-4552-bf7b-7a505a8c0b95"}
        ),
        (
                {"genre_name": "action"},
                {"status": http.HTTPStatus.OK, "name": "Action", "id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"}
        ),
        (
                {"genre_name": "animation"},
                {"status": http.HTTPStatus.OK, "name": "animation", "id": "6a0a479b-cfec-41ac-b520-41b2b007b611"}
        ),
        (
                {"genre_name": "war"},
                {"status": http.HTTPStatus.NOT_FOUND}
        )
    ]
)
async def test_list(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/genres/{query_data['genre_name']}"

    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == expected_answer["status"]
    if status == http.HTTPStatus.OK:
        assert body["name"].lower() == expected_answer["name"].lower()
        assert body["uuid"] == expected_answer["id"]


async def test_no_genre(fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    genre = None
    url = settings.app_url + f"/api/v1/genres/{genre}"

    async with session.get(url, params=None) as response:
        status = response.status
    await session.close()

    assert status == http.HTTPStatus.UNPROCESSABLE_ENTITY
