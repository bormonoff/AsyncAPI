from pydantic import BaseModel


class Person(BaseModel):
    id: str
    full_name: str
