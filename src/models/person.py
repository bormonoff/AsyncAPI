from typing import List

import pydantic


class PersonFilm(pydantic.BaseModel):
    uuid: str = pydantic.Field(alias="id")
    roles: List[str]


class PersonBase(pydantic.BaseModel):
    uuid: str = pydantic.Field(alias="id")
    full_name: str = pydantic.Field(alias="name")

class Person(PersonBase):
    films: List[PersonFilm]