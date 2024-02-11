import aiohttp
import pytest
from settings import settings


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44"},
                {"status": 200, "name": "Angela Turner", "id": "420155f3-c732-4c63-a668-daedc14fac44",
                 "films_count": 6, "max_roles": 1}
        ),
        (
                {"person_id": "b2c79ddc-fc3d-410a-b9c9-7b5792b62630"},
                {"status": 200, "name": "Gilby Clarke", "id": "b2c79ddc-fc3d-410a-b9c9-7b5792b62630",
                 "films_count": 6, "max_roles": 2}
        )
    ]
)
@pytest.mark.asyncio
async def test_person_info(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/persons/{query_data['person_id']}"
    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()
    print(body)
    assert status == expected_answer["status"]
    assert body["name"] == expected_answer["name"]
    assert body["id"] == expected_answer["id"]
    assert len(body["films"]) == expected_answer["films_count"]
    assert max(len(rec["roles"]) for rec in body["films"]) == expected_answer["max_roles"]


@pytest.mark.parametrize(
    "query_data, expected_answer",
    [
        (
                {"person_id": "420155f3-c732-4c63-a668-daedc14fac44"},
                {"status": 200}
        ),
        (
                {"person_id": "00000000-0000-0000-0000-000000000000"},
                {"status": 404}
         )
    ]
)
@pytest.mark.asyncio
async def test_person_exist(query_data, expected_answer, fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    url = settings.app_url + f"/api/v1/persons/{query_data['person_id']}"
    async with session.get(url) as response:
        body = await response.json()
        status = response.status
    await session.close()
    assert status == expected_answer["status"]


@pytest.mark.asyncio
async def test_no_person_id(fill_elastic):
    """Tests that API returns the correct paginated list of genres."""
    session = aiohttp.ClientSession()
    person = None
    url = settings.app_url + f"/api/v1/genres/{person}"
    async with session.get(url, params=None) as response:
        body = await response.json()
        status = response.status
    await session.close()
    assert status == 422
