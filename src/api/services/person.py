
import functools
from typing import Any

import elasticsearch
import fastapi
from redis import asyncio

from db import elastic, redis
from models import person as personmodel
from services import cache


class PersonService:
    def __init__(self, redis: asyncio.Redis, elastic: elasticsearch.AsyncElasticsearch):
        self.elastic = elastic
        self.cache_service = cache.CacheService(redis)

    async def get_persons_with_pattern(self, pattern: str, page_size: int, page_number: int
    ) -> list[personmodel.Person]:
        """Return a list of the persons with the pattern.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., fullname: ..., films: [{uuid}, roles: []], ...]

        """
        request = {
            "index": "persons",
            "size": page_size,
            "from_": page_size * (page_number - 1),
            "query": {"match": {"fullname": pattern}},
        }
        data = await self.elastic.search(**request)
        if not data["hits"]["hits"]:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        result = [self._transform_movie(movie["_source"]) for movie in data.body["hits"]["hits"]]
        return result

    async def get_person_with_id(self, person_id: str) -> personmodel.Person:

        person = await self.cache_service.get_entity_from_cache("person", person_id)
        if not person:
            person = await self.elastic.get(index="persons", id=person_id)
            if not person:
                raise fastapi.HTTPException(status_code=404, detail="Not found")
            person = self._transform_movie(person["_source"])
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
        elastic: elasticsearch.AsyncElasticsearch = fastapi.Depends(elastic.get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)

