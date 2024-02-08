import uuid
from typing import Annotated

import fastapi
from models import film as filmmodel
from models import person as personmodel
from services import film as filmservice
from services import person as personservice

router = fastapi.APIRouter()


@router.get("/search/", response_model=list[personmodel.Person])
async def search_persons(
    pattern: str,
    page_size: Annotated[int, fastapi.Query(description='Pagination page size', ge=1)] = 10,
    page_number: Annotated[int, fastapi.Query(description='Page number', ge=1)] = 1,
    person_service: personservice.PersonService = fastapi.Depends(personservice.get_person_service)
) -> list[personmodel.Person]:
    """Get the list of the films with the person and return the data to a client."""
    persons = await person_service.get_persons_with_pattern(
        pattern=pattern,
        page_size=page_size,
        page_number=page_number)
    return persons


@router.get("/{person_id}", response_model=personmodel.Person)
async def person_details(
    person_id: uuid.UUID,
    person_service: personservice.PersonService = fastapi.Depends(personservice.get_person_service)
) -> personmodel.Person:
    """Get the person data using person id and return the data to a client."""
    person = await person_service.get_person_with_id(person_id)
    return person


@router.get("/{person_id}/film", response_model=list[filmmodel.FilmBase])
async def search_films(
    person_id: uuid.UUID,
    page_size: Annotated[int, fastapi.Query(description='Pagination page size', ge=1)] = 10,
    page_number: Annotated[int, fastapi.Query(description='Page number', ge=1)] = 1,
    film_service: personservice.PersonService = fastapi.Depends(filmservice.get_film_service)
) -> list[filmmodel.FilmBase]:
    """Get all films with a person and return the data to a client."""

    films = await film_service.get_films_with_person(
        person_id=person_id,
        page_size=page_size,
        page_number=page_number)
    return films


@router.get("/{person_id}/film", response_model=list[filmmodel.FilmBase])
async def person_films(
    person_id: uuid.UUID,
    person_service: personservice.PersonService = fastapi.Depends(personservice.get_person_service),
    film_service: filmservice.FilmService = fastapi.Depends(filmservice.get_film_service)
) -> list[filmmodel.FilmBase]:
    """Get all films with a person and return the data to a client."""
    person = await person_service.get_person_with_id(person_id)
    films = person.films
    result = []
    for film in films:
        next_film = await film_service.get_by_id(film.uuid)
        result.append(next_film)
    return result
