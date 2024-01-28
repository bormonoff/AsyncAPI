from pydantic import BaseModel

from api.v1.genres import Genre
from api.v1.persons import Person


class FilmBase(BaseModel):
    uuid: str
    title: str
    imdb_rating: float | None


class Film(FilmBase):
    description: str | None
    genre: list[Genre]
    director: list[str]
    actor_names: list[str]
    wtiters_names: list[str]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]