"""Model for ETL objets"""
import datetime
import uuid

import pydantic


class UUIDMixin(pydantic.BaseModel):
    id: uuid.UUID


class Genre(UUIDMixin):
    name: str


class Person(UUIDMixin):
    name: str


class FilmWork(UUIDMixin):
    """Model for film work"""
    title: str
    description: str | None
    rating: float | None
    type: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime

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
