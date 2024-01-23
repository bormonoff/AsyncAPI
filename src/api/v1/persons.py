from pydantic import BaseModel
from typing import Optional


class Person(BaseModel):
    id: str
    full_name: str
    