from functools import lru_cache
from typing import Optional, Dict, List, Any, Tuple

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from redis.asyncio import Redis
from db.elastic import get_elastic
from db.redis import get_redis


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_persons_with_pattern(self, pattern: str, page_size: int,
                                     page_number: int
    ) -> List[Dict[str, str]]:
        """Return a list of the persons with the pattern.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., fullname: ..., films: [{uuid}, roles: []], ...]

        """
        pattern = pattern.lower()
        request = {
            "index": "movies",
            "size": page_size,
            "from_": page_size * (page_number - 1),
            "query": {"match": {"actors_names": pattern}},
        }
        data = await self.elastic.search(**request)
        # buffer = dict
        result = [self._transform_movie(movie["_source"], pattern) for movie in data.body["hits"]["hits"]]
        return result

    def _transform_movie(self, movie: Dict[str, Any], pattern: str) -> Dict[str, Any]:
        person = self._find_target_person(movie, pattern)
        result = {
            "uuid": movie["id"],
            "fullname": person["fullname"],
            "films": list()
        }
        for role in person["roles"]:
            retul


        result["fullname"] = movie["title"]
        result["imdb_rating"] = movie["imdb_rating"]
        return result

    def _find_target_person(self, movie: Dict[str, Any], pattern: str) -> Dict[str, List[str]]:
        """Find a person's fullname and roles in the movie."""

        # Brute search. As an initial data we gain a movie with the different roles.
        # As a result we find a person and his roles in the movie.
        # TODO refactor after changing elasticsearch indexes
        persons = {"actors_names": "actor",
                   "writers_names": "writer",
                   "director": "director"}
        data = {"roles": list()}
        for list_of_persons in persons.keys():
            for person in movie[list_of_persons]:
                if pattern in person.lower():
                    data["fullname"] = person
                    data["roles"].append(persons[list_of_persons])
                    break
        return data


# Use lru_cache decorator to gain service object as a singleton
@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)

