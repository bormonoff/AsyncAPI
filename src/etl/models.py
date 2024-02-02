import uuid
from datetime import datetime

from pydantic import BaseModel


class UUIDMixin(BaseModel):
    id: uuid.UUID


class Genre(UUIDMixin):
    name: str


class Person(UUIDMixin):
    name: str


class FilmWork(UUIDMixin):
    title: str
    description: str | None
    rating: float | None
    type: str | None
    created_at: datetime
    updated_at: datetime

    genres: list[Genre]
    directors: list[Person]
    actors: list[Person]
    writers: list[Person]

    genres_names: list[str]
    directors_names: list[str]
    actors_names: list[str]
    writers_names: list[str]


class ExtendedPerson(Person):
    films: list[dict]
