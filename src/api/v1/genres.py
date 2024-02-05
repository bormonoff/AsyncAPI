from typing import List

import fastapi

from models import genre as genremodel
from services import genre as genresevice

router = fastapi.APIRouter()


@router.get("/", response_model=List[genremodel.Genre], response_model_by_alias=False)
async def search_genres(
    page_size: int = 10,
    page_number: int = 1,
    genre_service: genresevice.GenreService = fastapi.Depends(genresevice.get_genre_service)
) -> List[genremodel.Genre]:
    """Get the list of the genres and return the data to a client."""
    films = await genre_service.get_genres(
        page_size=page_size,
        page_number=page_number)
    return films

@router.get("/{genre_id}", response_model=genremodel.Genre, response_model_by_alias=False)
async def search_films_using_genre(
    genre_id: str,
    page_size: int = 10,
    page_number: int = 1,
    genre_service: genresevice.GenreService = fastapi.Depends(genresevice.get_genre_service)
) -> genremodel.Genre:
    """Get genre info using genre uuid and return the data to a client."""
    genres = await genre_service.get_genres(
        genre_id=genre_id,
        page_size=page_size,
        page_number=page_number)
    return genres