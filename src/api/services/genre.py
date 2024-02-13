import functools
from typing import Union

import fastapi
from db import redis, storage
from models import genre as genremodel
from redis import asyncio


class GenreService:
    def __init__(self, redis: asyncio.Redis, storage: storage.BaseStorage):
        self.storage = storage
        self.redis = redis

    async def get_genres(self, page_size: int, page_number: int, genre_name: str = ""
    ) -> Union[genremodel.Genre, list[genremodel.Genre]]:
        """Return genres. Optionaly genre using a name.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., name: ...}, ...]

        """
        data = await self.storage.search(
            location="genres",
            page_size=page_size,
            page_number=page_number,
            genre_name=genre_name
        )
        if genre_name:
            return genremodel.Genre(**data[0]["_source"])
        result = [genremodel.Genre(**movie["_source"]) for movie in data]
        return result

# Use lru_cache decorator to gain service object as a singleton
@functools.lru_cache()
def get_genre_service(
    redis: asyncio.Redis = fastapi.Depends(redis.get_redis),
) -> GenreService:
    return GenreService(redis, storage.ElasticStorage())

