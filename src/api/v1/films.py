import http
from typing import List, Optional

import fastapi

from models import film as filmmodel
from services import film as filmservice

router = fastapi.APIRouter()


@router.get("/{film_id}", response_model=filmmodel.Film)
async def film_details(film_id: str,
                       film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service)
) -> filmmodel.Film:
    """Find and return the film wia it"s id."""
    film = await film_service.get_by_id(film_id)
    if not film:
        raise fastapi.HTTPException(status_code=http.HTTPStatus.NOT_FOUND, detail="film not found")
    return film

@router.get("/", response_model=List[filmmodel.FilmBase])
async def get_popular_films(sort: str = "imdb_rating",
                            genre: Optional[str] = None,
                            page_size: int = 10,
                            page_number: int = 1,
                            film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service)
) -> List[filmmodel.FilmBase]:
    """Get the list of the films sorted by a field_to_sort variable and return the data to a client."""
    films = await film_service.get_films_sorted_by_field(sort, genre, page_size, page_number)
    return films

@router.get("/search/", response_model=List[filmmodel.FilmBase])
async def search_films(pattern: str = "star",
                       page_size: int = 10,
                       page_number: int = 1,
                       film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service)
) -> List[filmmodel.FilmBase]:
    """Get the list of the films with the pattern in the title and return the data to a client."""
    films = await film_service.get_films_with_pattern(pattern, page_size, page_number)
    return films

