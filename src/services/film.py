from functools import lru_cache
from typing import Optional, Dict, List, Any
import uuid
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from redis.asyncio import Redis
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 min

def transform_movie(movie: Dict[str, Any]) -> Dict[str, Any]:
    result = {}
    result["uuid"] = movie["id"]
    result["title"] = movie["title"]
    result["imdb_rating"] = movie["imdb_rating"]
    return result


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """Optionally return a film from ES."""
        # TODO create redis cache
        # film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def get_films_sorted_by_field(self, field_to_sort: str, genre: Optional[str], page_size: int, page_number: int):
        """Return a list of the films sorted by a field_to_sort variable.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., title: ..., imdb_rating}, ...]

        """
        request = {
            "index": "movies",
            "size": page_size,
            "from_": page_size * (page_number - 1),
            "source": ["id", "title", "imdb_rating"],
            "sort": {field_to_sort: {"order": "desc"}},
            }
        if genre:
            request["query"] = {"match": {"genre": genre}}
        data = await self.elastic.search(**request)
        result = [transform_movie(movie["_source"]) for movie in data.body["hits"]["hits"]]
        return result

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.model_validate_json(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        # Redis set func doc: https://redis.io/commands/set/
        await self.redis.set(film.id, film.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)


# Use lru_cache decorator to gain service object as a singleton
@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
