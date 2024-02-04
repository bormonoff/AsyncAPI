import uuid
from typing import List

import fastapi

from models import film as filmmodel
from models import person as personmodel
from services import film as filmservice
from services import person as personservice

router = fastapi.APIRouter()


@router.get('/search/', response_model=List[personmodel.Person])
async def search_films(
    pattern: str,
    page_size: int = 10,
    page_number: int = 1,
    person_service: personservice.PersonService = fastapi.Depends(personservice.get_person_service)
) -> List[personmodel.Person]:
    """Get the list of the films with the person and return the data to a client."""
    films = await person_service.get_persons_with_pattern(
        pattern=pattern,
        page_size=page_size,
        page_number=page_number)
    return films

@router.get('/{person_id}', response_model=personmodel.Person)
async def search_films(
    person_id: str,
    person_service: personservice.PersonService = fastapi.Depends(personservice.get_person_service)
) -> personmodel.Person:
    """Get the person data using person id and return the data to a client."""
    try:
        uuid.UUID(person_id)
    except:
        raise fastapi.exceptions.RequestValidationError("Invalid uuid")
    films = await person_service.get_person_with_id(person_id)
    return films

@router.get('/{person_id}/film', response_model=List[filmmodel.FilmBase])
async def search_films(
    person_id: str,
    page_size: int = 10,
    page_number: int = 1,
    film_service: personservice.PersonService = fastapi.Depends(filmservice.get_film_service)
) -> List[filmmodel.FilmBase]:
    """Get all films with a person and return the data to a client."""
    try:
        uuid.UUID(person_id)
    except:
        raise fastapi.exceptions.RequestValidationError("Invalid uuid")
    films = await film_service.get_films_with_person(
        person_id=person_id,
        page_size=page_size,
        page_number=page_number)
    return films
