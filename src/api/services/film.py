import functools
from typing import Any, Optional

import fastapi
from db import elastic, redis
from models import film as filmmodel
from models import genre as genremodel
from models import person as personmodel
from redis import asyncio
from services import cache
from services.base import BaseService
from db.search_engine import AsyncSearchEngine, ElasticAsyncSearchEngine


class FilmService(BaseService):
    def __init__(self, redis: asyncio.Redis,
                 search_engine: ElasticAsyncSearchEngine):
        super().__init__(search_engine)
        self.cache_service = cache.CacheService(redis)

    async def get_by_id(self, film_id: str) -> Optional[filmmodel.Film]:
        """Optionally return a film from ES."""
        film = await self.cache_service.get_entity_from_cache("film", film_id)
        if not film:
            film = await self.search_engine.get_by_id(index="movies", _id=film_id)
            if not film:
                raise fastapi.HTTPException(status_code=404, detail="Not found")
            # film = filmmodel.Film.model_validate(film)
            film = self._handle_single_movie(film)
            await self.cache_service.put_entity_to_cache("movies", film)
        return film

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
                field_to_sort=field_to_sort, genre=genre
            )
            data = await self.search_engine.search(index="movies", query=request,
                                                   page_size=page_size, page_number=page_number
                                                   )
            if not data:
                raise fastapi.HTTPException(status_code=404, detail="Not found")
            films = [filmmodel.FilmBase.model_validate(el) for el in data]
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
        request = self._create_request(pattern=pattern)
        data = await self.search_engine.search(index="movies", query=request,
                                               page_size=page_size, page_number=page_number
                                               )
        if not data:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        films = [filmmodel.FilmBase.model_validate(el) for el in data]
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
        request = self._create_request(person_name=person_name)
        data = await self.search_engine.search(index="movies", query=request,
                                               page_size=page_size, page_number=page_number
                                               )
        if not data:
            raise fastapi.HTTPException(status_code=404, detail="Not found")
        films = [filmmodel.FilmBase.model_validate(el) for el in data]
        return films

    def _create_request(self, **kwargs) -> dict[str, str]:
        request = {
            # "index": "movies",
            "source": ["id", "title", "imdb_rating"],
        }

        if kwargs.get("field_to_sort"):
            request["sort"] = {kwargs["field_to_sort"]: {"order": "desc"}}
        if kwargs.get("genre"):
            request["query"] = {"match": {"genres_names": kwargs["genre"]}}
        if kwargs.get("pattern"):
            request["query"] = {"match": {"title": kwargs["pattern"]}}
        if kwargs.get("person_name"):
            request["query"] = {
                "bool": {
                    "should": [
                        {"match": {"directors_names": kwargs["person_name"]}},
                        {"match": {"actors_names": kwargs["person_name"]}},
                        {"match": {"writers_names": kwargs["person_name"]}},
                    ]
                }
            }
        return request


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
        elastic: AsyncSearchEngine = fastapi.Depends(ElasticAsyncSearchEngine),
) -> FilmService:
    return FilmService(redis, elastic)
