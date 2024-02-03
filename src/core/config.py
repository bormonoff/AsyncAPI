import os

import pydantic_settings
import logging

from core import logger

logging.config.dictConfig(logger.LOGGING)


class Settings(pydantic_settings.BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    ELASTIC_DSN: str
    ELASTIC_INDEX: str
    PROJECT_NAME: str
    ELASTIC_HOST: str
    ELASTIC_PORT: int
    REDIS_HOST: str
    REDIS_PORT: int


    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
