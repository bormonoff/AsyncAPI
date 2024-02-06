import pydantic
from models import genre as genremodel
from models import person as personmodel


class FilmBase(pydantic.BaseModel):
    uuid: str = pydantic.Field(alias="id")
    title: str
    imdb_rating: float | None


class Film(FilmBase):
    description: str | None
    genre: list[genremodel.Genre]
    actors: list[personmodel.PersonBase]
    writers: list[personmodel.PersonBase]
    directors: list[personmodel.PersonBase]
