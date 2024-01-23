from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.film import FilmService, get_film_service
from .genres import Genre
from .persons import Person

# Объект router, в котором регистрируем обработчики
router = APIRouter()

# Модель ответа API
class Film(BaseModel):
    id: str
    title: str
    description: str | None
    imdb_rating: float | None
    genre: list[Genre]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]


# С помощью декоратора регистрируем обработчик film_details
# На обработку запросов по адресу <some_prefix>/some_id
# Позже подключим роутер к корневому роутеру 
# И адрес запроса будет выглядеть так — /api/v1/film/some_id
@router.get('/{film_id}', response_model=Film)
# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=Film)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
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
