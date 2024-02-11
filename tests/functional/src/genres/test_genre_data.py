import aiohttp
import pytest
from settings import settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"genre_name": "History"},
                {"status": 200, "name": "History", "id": "eb7212a7-dd10-4552-bf7b-7a505a8c0b95"}
        ),
        (
                {"genre_name": "action"},
                {"status": 200, "name": "Action", "id": "3d8d9bf5-0d90-4353-88ba-4ccc5d2c07ff"}
        ),
        (
                {"genre_name": "animation"},
                {"status": 200, "name": "animation", "id": "6a0a479b-cfec-41ac-b520-41b2b007b611"}
        ),
        (
                {"genre_name": "war"},
                {"status": 404}
        )
    ]
)
@pytest.mark.asyncio
async def test_list(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/genres/{query_data['genre_name']}"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    print(body)
    assert status == expected_answer["status"]
    if status == 200:
        assert body["name"].lower() == expected_answer["name"].lower()
        assert body["uuid"] == expected_answer["id"]
