from pydantic import BaseModel
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from services.person import PersonService, get_person_service

from typing import List, Dict

router = APIRouter()


class Person(BaseModel):
    uuid: str
    full_name: str
    films: List[Dict[str, str]]


@router.get('/search/', response_model=List[Person])
async def search_films(pattern: str = "captain",
                       page_size: int = 10,
                       page_number: int = 1,
                       person_service: PersonService = Depends(get_person_service)
) -> List[Person]:
    """Get the list of the films with the pattern in the title and return the data to a client."""
    films = await person_service.get_persons_with_pattern(pattern, page_size, page_number)
    return films