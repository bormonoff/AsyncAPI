import functools
from typing import Any, Optional

import elasticsearch
import fastapi
from db import elastic, redis
from models import film as filmmodel
from models import genre as genremodel
from models import person as personmodel
from redis import asyncio
from services import cache

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 min


class FilmService:
    def __init__(self, redis: asyncio.Redis, elastic: elasticsearch.AsyncElasticsearch):
        self.elastic = elastic
        self.cache_service = cache.CacheService(redis)

    async def get_by_id(self, film_id: str) -> Optional[filmmodel.Film]:
        """Optionally return a film from ES."""
        film = await self.cache_service.get_entity_from_cache("film", film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            await self.cache_service.put_entity_to_cache("film", film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[filmmodel.Film]:
        try:
            data = await self.elastic.get(index="movies", id=film_id)
        except elasticsearch.NotFoundError:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        return self._handle_single_movie(data["_source"])

    async def get_films_sorted_by_field(
        self,
        field_to_sort: str,
        genre: Optional[str],
        page_size: int,
        page_number: int
    ) -> list[filmmodel.FilmBase]:
        """Return a list of the films sorted by a sort variable.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., title: ..., imdb_rating}, ...]

        """
        field_to_filter = "all" if not genre else genre
        films = await self.cache_service.get_list_from_cache("base_film", field_to_filter, field_to_sort,
                                                             page_size, page_number)
        if not films:
            request = self._create_request(
                page_size=page_size, page_number=page_number,
                field_to_sort=field_to_sort, genre=genre
            )
            films = await self._get_filmbase_list(request)
            if not films:
                return None
            await self.cache_service.put_list_to_cache("base_film", field_to_filter, field_to_sort,
                                                       page_size, page_number, films)
        return films

    async def get_films_with_pattern(
        self,
        pattern: str,
        page_size: int,
        page_number: int
    ) -> list[filmmodel.FilmBase]:
        """Return a list of the films with the pattern.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., title: ..., imdb_rating}, ...]

        """
        request = self._create_request(page_size=page_size, page_number=page_number, pattern=pattern)
        result = await self._get_filmbase_list(request)
        return result

    async def get_films_with_person(
        self,
        person_id: str,
        page_size: int,
        page_number: int
    ) -> list[filmmodel.FilmBase]:
        """Return a list of the films with the person using person_id.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., title: ..., imdb_rating}, ...]

        """
        request = self._create_request(page_size=page_size, page_number=page_number, person_id=person_id)
        result = await self._get_filmbase_list(request)
        return result

    async def _get_filmbase_list(self, request) -> list[filmmodel.FilmBase]:
        try:
            data = await self.elastic.search(**request)
        except elasticsearch.BadRequestError as ex:
            raise fastapi.HTTPException(status_code=400, detail=str(ex))
        result = [self._handle_movie(movie["_source"]) for movie in data.body["hits"]["hits"]]
        if not result:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        return result

    def _create_request(self, **kwargs) -> dict[str, str]:
        request = {
            "index": "movies",
            "size": kwargs["page_size"],
            "from_": kwargs["page_size"] * (kwargs["page_number"] - 1),
            "source": ["id", "title", "imdb_rating"],
        }

        if kwargs.get("field_to_sort"):
            request["sort"] = {kwargs["field_to_sort"]: {"order": "desc"}}
        if kwargs.get("genre"):
            request["query"] = {"match": {"genre": kwargs["genre"]}}
        if kwargs.get("pattern"):
            request["query"] = {"match": {"title": kwargs["pattern"]}}
        if kwargs.get("person_id"):
            request["query"] = {"nested": {
                "path": "directors",
                "query": {
                    "match": {
                        "directors.id": kwargs["person_id"],
                        "actors.id": kwargs["person_id"],
                        "writers.id": kwargs["person_id"],
                    }
                }
            }}
        return request

    def _handle_movie(self, movie: dict[str, Any]) -> filmmodel.FilmBase:
        return filmmodel.FilmBase(
            id=movie["id"],
            title=movie["title"],
            imdb_rating=movie["imdb_rating"]
        )

    def _handle_single_movie(self, movie: dict[str, Any]) -> filmmodel.Film:
        return filmmodel.Film(
            id=movie["id"],
            title=movie["title"],
            imdb_rating=movie["imdb_rating"],
            description=movie["description"],
            genre=[genremodel.Genre(**data) for data in movie["genres"]],
            directors=[personmodel.PersonBase(**data) for data in movie["directors"]],
            actors=[personmodel.PersonBase(**data) for data in movie["actors"]],
            writers=[personmodel.PersonBase(**data) for data in movie["writers"]]
        )


# Use lru_cache decorator to gain service object as a singleton
@functools.lru_cache()
def get_film_service(
        redis: asyncio.Redis = fastapi.Depends(redis.get_redis),
        elastic: elasticsearch.AsyncElasticsearch = fastapi.Depends(elastic.get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
