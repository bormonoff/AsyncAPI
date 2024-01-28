from pydantic import BaseModel


class Genre(BaseModel):
    id: str
    name: str
