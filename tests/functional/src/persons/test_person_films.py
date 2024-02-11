import aiohttp
import pytest
from settings import settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44", "page_size": 10, "page_number": 1},
                {"status": 200, "length": 6}
        ),
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44", "page_size": 5, "page_number": 1},
                {"status": 200, "length": 5}
        ),
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44", "page_size": 5, "page_number": 2},
                {"status": 200, "length": 1}
        ),
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44", "page_size": 5, "page_number": 3},
                {"status": 200, "length": 0}
        )
    ]
)
@pytest.mark.asyncio
async def test_list(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/persons/{query_data['person_id']}/film"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    print(body)
    assert status == expected_answer["status"]
    assert len(body) == expected_answer["length"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"person_id": "00000000-0000-0000-0000-000000077534200000", "page_size": 5, "page_number": 1},
                {"status": 422}
        ),
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44", "page_size": 5, "page_number": -1},
                {"status": 422}
        )
    ]
)
@pytest.mark.asyncio
async def test_not_correct_data(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/persons/{query_data['person_id']}/film"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    assert status == expected_answer["status"]
