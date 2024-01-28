from pydantic import BaseModel


class FilmBase(BaseModel):
    uuid: str
    title: str
    imdb_rating: float | None


class Film(FilmBase):
    description: str | None
    director: str
    actors: list[str]
    writers: list[str]
    genre: list[str]