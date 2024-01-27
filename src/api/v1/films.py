from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from services.film import FilmService, get_film_service
from .genres import Genre
from .persons import Person

from typing import List, Optional

router = APIRouter()


class Film(BaseModel):
    id: str
    title: str
    description: str | None
    imdb_rating: float | None
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]


@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    """Find and return the film wia it's id."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(
        id=film.id,
        title=film.title,
        description=film.description,
        imdb_rating=film.imdb_rating,
        genre=film.genre,
        actors=film.actors,
        writers=film.writers,
        directors=film.directors
        )


class FilmBase(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


@router.get('/', response_model=List[FilmBase])
async def get_popular_films(sort: str,
                            genre: Optional[str] = None,
                            page_size: int = 10,
                            page_number: int = 1,
                            film_service: FilmService = Depends(get_film_service)
) -> list[FilmBase]:
    """Get the list of the films sorted by a field_to_sort variable and return the data to a client"""
    films = await film_service.get_films_sorted_by_field(sort, genre, page_size, page_number)
    return films
