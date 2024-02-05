import functools
from typing import List, Union

import elasticsearch
import fastapi
from redis import asyncio

from db import elastic, redis
from models import genre as genremodel


class GenreService:
    def __init__(self, redis: asyncio.Redis, elastic: elasticsearch.AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_genres(self, page_size: int, page_number: int, genre_id: str = ""
    ) -> Union[genremodel.Genre, List[genremodel.Genre]]:
        """Return genres. Optionaly genre using a name.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., name: ...}, ...]

        """
        data = await self.elastic.search(**self._create_request(
            page_size=page_size,
            page_number=page_number,
            genre_id=genre_id)
        )
        if not data["hits"]["hits"]:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        if genre_id:
            return genremodel.Genre(**data.body["hits"]["hits"][0]["_source"])
        result = [genremodel.Genre(**movie["_source"]) for movie in data.body["hits"]["hits"]]
        return result

    def _create_request(self, page_size: int, page_number: int, genre_id: str = ""):
        request = {
            "index": "genres",
            "size": page_size,
            "from_": page_size * (page_number - 1),
        }
        if genre_id:
            request["query"] = {"match": {"id": str(genre_id)}}
        return request


# Use lru_cache decorator to gain service object as a singleton
@functools.lru_cache()
def get_genre_service(
    redis: asyncio.Redis = fastapi.Depends(redis.get_redis),
    elastic: elasticsearch.AsyncElasticsearch = fastapi.Depends(elastic.get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)

