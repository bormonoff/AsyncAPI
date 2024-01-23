import orjson
from pydantic import BaseModel
from uuid import UUID

def orjson_dumps(v, *, default):
    # orjson.dumps возвращает bytes, а pydantic требует unicode, поэтому декодируем
    return orjson.dumps(v, default=default).decode()


class UUIDMixin(BaseModel):
    id: str

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(UUIDMixin):
    full_name: str
    # films: list[Film]


class Genre(UUIDMixin):
    name: str


class Film(UUIDMixin):
    title: str
    description: str | None
    imdb_rating: float | None
    genre: list[Genre]
    director: list[str]
    actor_names: list[str]
    wtiters_names: list[str]
    actors: list[Person]
    writers: list[Person]
    directors: list[Person]
