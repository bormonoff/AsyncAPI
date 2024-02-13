import functools
from typing import Any

import fastapi
from db import redis, storage
from models import person as personmodel
from redis import asyncio
from services import cache


class PersonService:
    def __init__(self, redis: asyncio.Redis, storage: storage.BaseStorage):
        self.storage = storage
        self.cache_service = cache.CacheService(redis)

    async def get_persons_with_pattern(self, pattern: str, page_size: int, page_number: int
    ) -> list[personmodel.Person]:
        """Return a list of the persons with the pattern.

        Returnes data as a following list:
        [{uuid: ..., fullname: ..., films: [{uuid}, roles: []], ...]

        """
        data = await self.storage.search(
            location="persons",
            page_size=page_size,
            page_number=page_number,
            full_name=pattern
        )
        result = [self._transform_movie(movie["_source"]) for movie in data]
        return result

    async def get_person_with_id(self, person_id: str) -> personmodel.Person:
        person = await self.cache_service.get_entity_from_cache("person", person_id)
        if not person:
            person = await self.storage.get_by_id(location="persons", id=person_id)
            person = self._transform_movie(person)
            await self.cache_service.put_entity_to_cache("person", person)
        return person

    def _transform_movie(self, movie: dict[str, Any]) -> personmodel.Person:
        return personmodel.Person(
            id=movie["id"],
            name=movie["fullname"],
            films=[personmodel.PersonFilm(**movie) for movie in movie["films"]]
        )


# Use lru_cache decorator to gain service object as a singleton
@functools.lru_cache()
def get_person_service(
        redis: asyncio.Redis = fastapi.Depends(redis.get_redis),
) -> PersonService:
    return PersonService(redis, storage.ElasticStorage())

