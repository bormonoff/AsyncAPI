import os

import pydantic_settings


class Settings(pydantic_settings.BaseSettings):
    app_url: str
    elastic_host: str
    elastic_port: str
    elastic_dsn: str
    elastic_indexes: str
    redis_host: str
    redis_port: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
