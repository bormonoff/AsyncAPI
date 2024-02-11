import abc

import elasticsearch
from core.config import settings


class BaseStorage(abc.ABC):
    """Abstract class for getting data from some storage"""

    connection = None

    def __init__(self) -> None:
        self.init_connection()

    @abc.abstractmethod
    def init_connection(self) -> None:
        """Connection initialization to storage"""

    @abc.abstractmethod
    async def get_by_id(self, location: str, _id: str) -> dict:
        """Getting object by id"""

    @abc.abstractmethod
    async def search(
        self, location: str, query: dict, page_size: int | None = None, page_number: int = 0
    ) -> list[dict]:
        """Searching objects by some query with pagination"""


class BaseMoviesStorage(BaseStorage, metaclass=abc.ABCMeta):
    """Abstract class for getting movies data from some storage"""

    FILMS_LOCATION = None
    PERSONS_LOCATION = None
    GENRES_LOCATION = None

    async def get_film_by_id(self, film_id: str) -> dict | None:
        """Getting film object by id"""
        return await self.get_by_id(self.FILMS_LOCATION, film_id)

    async def get_person_by_id(self, person_id: str) -> dict | None:
        """Getting person object by id"""
        return await self.get_by_id(self.PERSONS_LOCATION, person_id)

    @staticmethod
    @abc.abstractmethod
    def _get_person_fullname_query(pattern: str) -> dict:
        """Getting query params to fild person by fullname"""

    async def search_persons_by_fullname(self, pattern: str, page_size: int | None = None, page_number: int = 0) -> list[dict]:
        query = self._get_person_fullname_query(pattern)
        return await self.search(self.PERSONS_LOCATION, query=query, page_size=page_size, page_number=page_number)


class ElasticStorage(BaseStorage):
    """Class for getting data from Elasticsearch"""

    def init_connection(self) -> None:
        self.connection = elasticsearch.AsyncElasticsearch(settings.ELASTIC_DSN)

    async def get_by_id(self, location: str, _id: str) -> dict | None:
        try:
            result = await self.connection.get(index=location, id=_id)
        except elasticsearch.NotFoundError:
            return
        return result["_source"]

    async def search(
        self, location: str, query: dict, page_size: int | None = None, page_number: int = 0
    ) -> list[dict]:
        request = {
            "index": location,
            "query": query,
        }
        if page_size:
            request.update({"size": page_size, "from_": page_size * (page_number - 1)})

        result = await self.connection.search(**request)
        return [i["_source"] for i in result["hits"]["hits"]]


class ElasticMoviesStorage(BaseMoviesStorage, ElasticStorage):
    FILMS_LOCATION = "movies"
    PERSONS_LOCATION = "persons"
    GENRES_LOCATION = "genres"

    @staticmethod
    def _get_person_fullname_query(pattern: str) -> dict:
        return {"match": {"fullname": pattern}}
