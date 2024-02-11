from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN: str
    ELASTIC_DSN: str
    ELASTIC_INDEXES: str
    FILM_WORK_CHUNK_SIZE: int
    GENRE_CHUNK_SIZE: int
    PERSON_CHUNK_SIZE: int
    LOAD_CHUNK_SIZE: int
    STATE_PATH: str
    SLEEP_TIME: int

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
