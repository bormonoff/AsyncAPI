import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # API
    ELASTIC_DSN: str
    ELASTIC_INDEXES: str
    PROJECT_NAME: str
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # ETL
    POSTGRES_DSN: str
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
