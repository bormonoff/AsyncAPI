import http

import aiohttp
import pytest
import settings

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "query_data, rating, expected_count",
    [
        (
            {"sort": "imdb_rating", "page_size": "6", "page_number": "1"},
            (9.9, 9.8, 9.7, 9.6, 8.9, 8.9),
            6
        ),
        (
            {"sort": "imdb_rating", "page_size": "3", "page_number": "1"},
            (9.9, 9.8, 9.7),
            3
        ),
        (
            {"sort": "imdb_rating", "genre": "horror", "page_size": "10", "page_number": "1"},
            (5.0, 4.9, 4.8, 4.2, 4.1, 4.0),
            6
        )
    ]
)
async def test_sort(query_data, rating, expected_count, fill_elastic):
    "Tests that API returns the correctly sorted data."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/"

    async with session.get(url, params=query_data) as response:
        body = await response.json()
        status = response.status
    await session.close()

    assert status == http.HTTPStatus.OK
    for i in range(expected_count):
        assert body[i]["imdb_rating"] == rating[i]


@pytest.mark.parametrize(
    "query_data",
    [
        (
            {"page_size": "-1", "page_number": "1"},
        ),
        (
            {"page_size": "6", "page_number": "-1"},
        ),
        (
            {"page_size": "0", "page_number": "1"},
        ),
        (
            {"page_size": "6", "page_number": "0"},
        ),
    ]
)
async def test_validation(query_data):
    "Tests that request data is invalid."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/"

    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()

    assert status == http.HTTPStatus.UNPROCESSABLE_ENTITY


async def test_unknown_genre():
    "Tests that unknown genre returns 404."
    session = aiohttp.ClientSession()
    url = settings.settings.app_url + "/api/v1/films/"
    query_data = {
        "sort": "imdb_rating",
        "genre": "unknown",
        "page_size": "10",
        "page_number": "1"
    }

    async with session.get(url, params=query_data) as response:
        status = response.status
    await session.close()

    assert status == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "query_data, body_count",
    [
        (
            {"sort": "imdb_rating", "genre": "horror", "page_size": "2", "page_number": "2"},
            2
        ),
        (
            {"sort": "imdb_rating", "genre": "horror", "page_size": "2", "page_number": "3"},
            2
        ),
        (
            {"sort": "imdb_rating", "genre": "horror", "page_size": "2", "page_number": "4"},
            1
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