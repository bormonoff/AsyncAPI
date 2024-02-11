import http
import uuid
from typing import Annotated

import fastapi
from models import film as filmmodel
from services import film as filmservice

router = fastapi.APIRouter()


@router.get("/{film_id}", response_model=filmmodel.Film, response_model_by_alias=False)
async def film_details(
    film_id: uuid.UUID, film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service)
) -> filmmodel.Film:
    """Find and return the film via its id."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise fastapi.HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="film not found")
    return film


@router.get("/", response_model=list[filmmodel.FilmBase], response_model_by_alias=False)
async def get_popular_films(
    sort: str = "imdb_rating",
    genre: str | None = None,
    page_size: Annotated[int, fastapi.Query(description="Pagination page size", ge=1)] = 10,
    page_number: Annotated[int, fastapi.Query(description="Page number", ge=1)] = 1,
    film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service),
) -> list[filmmodel.FilmBase]:
    """Get the list of the films sorted by a sort variable and return the data to a client."""
    films = await film_service.get_films_sorted_by_field(
        field_to_sort=sort, genre=genre, page_size=page_size, page_number=page_number
    )
    return films


@router.get("/search/", response_model=list[filmmodel.FilmBase], response_model_by_alias=False)
async def search_films(
    pattern: str,
    page_size: Annotated[int, fastapi.Query(description="Pagination page size", ge=1)] = 10,
    page_number: Annotated[int, fastapi.Query(description="Page number", ge=1)] = 1,
    film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service),
) -> list[filmmodel.FilmBase]:
    """Get the list of the films with the pattern in the title and return the data to a client."""
    films = await film_service.get_films_with_pattern(pattern=pattern, page_size=page_size, page_number=page_number)
    return films
