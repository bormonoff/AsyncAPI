import abc
from typing import Any

import elasticsearch

from core.config import settings


class AsyncSearchEngine(abc.ABC):
    @abc.abstractmethod
    async def get_by_id(self, index: str, _id: str) -> Any | None:
        pass

    @abc.abstractmethod
    async def search(self, index: str, query: dict, page_size: int, page_number: int) -> list[Any] | None:
        pass


class ElasticAsyncSearchEngine(AsyncSearchEngine):
    def __init__(self):
        self.connection = elasticsearch.AsyncElasticsearch(settings.ELASTIC_DSN)

    async def get_by_id(self, index: str, _id: str) -> dict | None:
        try:
            result = await self.connection.get(index=index, id=_id)
        except elasticsearch.NotFoundError:
            return
        return result["_source"]

    async def search(
        self, index: str, query: dict, page_size: int | None = None, page_number: int = 1
    ) -> list[dict] | None:
        request = query
        request.update({"index": index})
        if page_size:
            request.update({"size": page_size, "from_": page_size * (page_number - 1)})

        response = await self.connection.search(**request)
        result = [i["_source"] for i in response["hits"]["hits"]]
        return result
