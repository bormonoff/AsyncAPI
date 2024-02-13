import functools
from typing import Any, Optional

import elasticsearch
import fastapi
from db import redis, storage
from models import film as filmmodel
from models import genre as genremodel
from models import person as personmodel
from redis import asyncio
from services import cache

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 min


class FilmService:
    def __init__(self, redis: asyncio.Redis, storage: storage.BaseStorage):
        self.storage = storage
        self.cache_service = cache.CacheService(redis)

    async def get_by_id(self, film_id: str) -> Optional[filmmodel.Film]:
        """Optionally return a film from ES."""
        film = await self.cache_service.get_entity_from_cache("film", film_id)
        if not film:
            film = await self._get_film_from_storage(film_id)
            await self.cache_service.put_entity_to_cache("film", film)
        return film

    async def _get_film_from_storage(self, film_id: str) -> Optional[filmmodel.Film]:
        data = await self.storage.get_by_id(location="movies", id=film_id)
        return self._handle_single_movie(data)

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
            data = await self.storage.search(
                location="movies",
                page_size=page_size, page_number=page_number,
                field_to_sort=field_to_sort, genre=genre
            )
            films = [self._handle_movie(movie["_source"]) for movie in data]
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
        data = await self.storage.search(
            location="movies",
            page_size=page_size,
            page_number=page_number,
            pattern=pattern
        )
        films = [self._handle_movie(movie["_source"]) for movie in data]
        return films

    async def get_films_with_person(
        self,
        person_name: str,
        page_size: int,
        page_number: int
    ) -> list[filmmodel.FilmBase]:
        """Return a list of the films with the person using person_id.

        Encapsulates elastic specific format and returnes data as a following list:
        [{uuid: ..., title: ..., imdb_rating}, ...]

        """
        data = await self.storage.search(
            location="movies",
            page_size=page_size,
            page_number=page_number,
            person_name=person_name
        )
        films = [self._handle_movie(movie["_source"]) for movie in data]
        return films

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
        redis: asyncio.Redis = fastapi.Depends(redis.get_redis)
) -> FilmService:
    return FilmService(redis, storage.ElasticStorage())
