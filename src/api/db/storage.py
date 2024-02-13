import abc
from typing import Any

import elasticsearch
import fastapi
from core.config import settings


class BaseStorage(abc.ABC):
    """Abstract class for getting data from a storage"""

    connection = None

    @abc.abstractmethod
    async def get_connection(self) -> Any:
        "Get a storage connection."

    @abc.abstractmethod
    async def get_by_id(self, location: str, _id: str) -> dict:
        """Get object by id."""

    @abc.abstractmethod
    async def search(
        self, location: str, query: dict, page_size: int | None = None, page_number: int = 0
    ) -> list[dict]:
        """Search objects by some query"""


class ElasticStorage(BaseStorage):
    """Class for getting data from Elasticsearch"""
    def __init__(self) -> None:
        self.connection = elasticsearch.AsyncElasticsearch(settings.ELASTIC_DSN)

    async def get_connection(self) -> elasticsearch.AsyncElasticsearch:
        return self.connection

    async def get_by_id(self, location: str, id: str) -> dict | None:
        try:
            result = await self.connection.get(index=location, id=id)
        except elasticsearch.NotFoundError:
            return
        return result["_source"]

    async def search(
        self,
        location: str,
        page_size: int | None = None,
        field_to_sort: str | None = None,
        genre: str | None = None,
        pattern: str | None = None,
        person_name: str | None = None,
        genre_name: str | None = None,
        full_name: str | None = None,
        page_number: int = 0
    ) -> list[dict]:
        request = await self._create_request(
            location=location,
            page_size=page_size,
            field_to_sort=field_to_sort,
            genre=genre,
            pattern=pattern,
            person_name=person_name,
            page_number=page_number,
            genre_name=genre_name,
            full_name=full_name
        )
        try:
            result = await self.connection.search(**request)
        except elasticsearch.BadRequestError as ex:
            raise fastapi.HTTPException(status_code=400, detail=str(ex))
        if not result["hits"]["hits"]:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        return result["hits"]["hits"]

    async def _create_request(self, location, **kwargs):
        if location == "movies":
            request = await self._create_movies_request(**kwargs)
        elif location == "genres":
            request = await self._create_genre_request(**kwargs)
        elif location == "persons":
            request = await self._create_person_request(**kwargs)

        return request

    async def _create_movies_request(self, **kwargs) -> dict[str, str]:
        request = {
            "index": "movies",
            "size": kwargs["page_size"],
            "from_": kwargs["page_size"] * (kwargs["page_number"] - 1),
            "source": ["id", "title", "imdb_rating"],
        }

        if kwargs.get("field_to_sort"):
            request["sort"] = {kwargs["field_to_sort"]: {"order": "desc"}}
        if kwargs.get("genre"):
            request["query"] = {"match": {"genres_names": kwargs["genre"]}}
        if kwargs.get("pattern"):
            request["query"] = {"match": {"title": kwargs["pattern"]}}
        if kwargs.get("person_name"):
            request["query"] = {
                "bool": {
                    "should": [
                        {"match": {"directors_names": kwargs["person_name"]}},
                        {"match": {"actors_names": kwargs["person_name"]}},
                        {"match": {"writers_names": kwargs["person_name"]}},
                    ]
                }
            }
        return request

    async def _create_genre_request(self, **kwargs):
        request = {
            "index": "genres",
            "size": kwargs["page_size"],
            "from_": kwargs["page_size"] * (kwargs["page_number"] - 1),
        }
        if kwargs["genre_name"]:
            request["query"] = {"match": {"name": str(kwargs["genre_name"])}}
        return request

    async def _create_person_request(self, **kwargs):
        request = {
            "index": "persons",
            "size": kwargs["page_size"],
            "from_": kwargs["page_size"] * (kwargs["page_number"] - 1),
            "query": {"match": {"fullname": kwargs["full_name"]}},
        }
        return request


