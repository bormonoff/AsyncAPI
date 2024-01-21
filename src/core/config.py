from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from logging import config as logging_config

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    ELASTICSEARCH_DSN: str
    ELASTICSEARCH_INDEX: str
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
