import functools
from typing import Union

import fastapi
from db import elastic, redis
from models import genre as genremodel
from redis import asyncio

from db.search_engine import AsyncSearchEngine, ElasticAsyncSearchEngine
from services.base import BaseService

from services import cache


class GenreService(BaseService):
    def __init__(self, redis: asyncio.Redis,
                 search_engine: ElasticAsyncSearchEngine):
        super().__init__(search_engine)
        self.cache_service = cache.CacheService(redis)

    async def get_genre(self, genre_id: str) -> genremodel.Genre:
        genre = await self.cache_service.get_entity_from_cache("genre", genre_id)
        if not genre:
            genre = await self.search_engine.get_by_id(index="genres", _id=genre_id)
            if not genre:
                raise fastapi.HTTPException(status_code=404, detail="Not found")
            genre = genremodel.Genre.model_validate(genre)
            await self.cache_service.put_entity_to_cache("genre", genre)
        return genre

    async def get_genres(self, page_size: int, page_number: int) -> Union[genremodel.Genre, list[genremodel.Genre]]:
        data = await self.search_engine.search(index="genres", query={},
                                               page_size=page_size, page_number=page_number
                                               )
        if not data:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        result = [genremodel.Genre.model_validate(el) for el in data]
        return result


# Use lru_cache decorator to gain service object as a singleton
@functools.lru_cache()
def get_genre_service(
        redis: asyncio.Redis = fastapi.Depends(redis.get_redis),
        elastic: AsyncSearchEngine = fastapi.Depends(ElasticAsyncSearchEngine),
) -> GenreService:
    return GenreService(redis, elastic)
