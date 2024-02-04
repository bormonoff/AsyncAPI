import pydantic


class Genre(pydantic.BaseModel):
    uuid: str = pydantic.Field(alias="id")
    name: str

